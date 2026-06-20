from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from config import Config
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )


# -----------------------------
# LOGIN REQUIRED DECORATOR
# -----------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'user_id' not in session:
            flash("Please login first", "warning")
            return redirect(url_for('login'))

        return f(*args, **kwargs)

    return decorated_function


# -----------------------------
# FILE VALIDATION
# -----------------------------

def allowed_file(filename):

    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower()
        in Config.ALLOWED_EXTENSIONS
    )


# -----------------------------
# SAVE FILE
# -----------------------------

def save_uploaded_file(file):

    if not file:
        return None

    if file.filename == '':
        return None

    if not allowed_file(file.filename):
        return None

    extension = file.filename.rsplit('.', 1)[1].lower()

    unique_filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )

    filename = secure_filename(unique_filename)

    if extension == "pdf":
        folder = Config.PDF_FOLDER

    elif extension in ["doc", "docx"]:
        folder = Config.DOC_FOLDER

    elif extension in ["ppt", "pptx"]:
        folder = Config.PPT_FOLDER

    else:
        folder = Config.IMAGE_FOLDER

    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, filename)

    file.save(file_path)

    return file_path


# -----------------------------
# HOME PAGE
# -----------------------------

@app.route('/')
def home():
    return render_template("home.html")


# -----------------------------
# REGISTER
# -----------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        role = request.form.get("role")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not email.endswith(Config.VVCE_EMAIL_DOMAIN):
            flash(
                "Only VVCE emails are allowed.",
                "danger"
            )
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            if role == "student":

                usn = request.form.get("usn")
                branch = request.form.get("branch")
                year = request.form.get("year")
                semester = request.form.get("semester")

                query = """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role,
                    usn,
                    branch,
                    year,
                    semester
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """

                values = (
                    name,
                    email,
                    hashed_password,
                    role,
                    usn,
                    branch,
                    year,
                    semester
                )

            else:

                professor_id = request.form.get(
                    "professor_id"
                )

                query = """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role,
                    professor_id
                )
                VALUES (%s,%s,%s,%s,%s)
                """

                values = (
                    name,
                    email,
                    hashed_password,
                    role,
                    professor_id
                )

            cursor.execute(query, values)
            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(url_for('login'))

        except mysql.connector.Error as e:

            flash(
                f"Registration failed: {e}",
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

    return render_template("register.html")


# -----------------------------
# LOGIN
# -----------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT *
        FROM users
        WHERE email = %s
        """

        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(
            user['password'],
            password
        ):

            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['role'] = user['role']

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for('dashboard')
            )

        flash(
            "Invalid credentials.",
            "danger"
        )

    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------

@app.route('/logout')
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(url_for('home'))


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route('/dashboard')
@login_required
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM users
        WHERE role='student'
    """)
    total_students = cursor.fetchone()['total_students']

    cursor.execute("""
        SELECT COUNT(*) AS total_professors
        FROM users
        WHERE role='professor'
    """)
    total_professors = cursor.fetchone()['total_professors']

    cursor.execute("""
        SELECT COUNT(*) AS total_materials
        FROM materials
    """)
    total_materials = cursor.fetchone()['total_materials']

    cursor.execute("""
        SELECT COUNT(*) AS total_requests
        FROM requests
    """)
    total_requests = cursor.fetchone()['total_requests']

    cursor.execute("""
        SELECT
            m.material_id,
            m.title,
            m.description,
            m.upload_date,
            s.subject_name,
            u.name AS uploader
        FROM materials m
        JOIN subjects s
            ON m.subject_id = s.subject_id
        JOIN users u
            ON m.uploaded_by = u.user_id
        ORDER BY m.upload_date DESC
        LIMIT 10
    """)

    recent_materials = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_professors=total_professors,
        total_materials=total_materials,
        total_requests=total_requests,
        recent_materials=recent_materials
    )


# -----------------------------
# UPLOAD MATERIAL
# -----------------------------

@app.route('/upload_material', methods=['GET', 'POST'])
@login_required
def upload_material():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        title = request.form.get("title")
        description = request.form.get("description")
        year = request.form.get("year")
        semester = request.form.get("semester")
        subject_id = request.form.get("subject_id")
        youtube_link = request.form.get("youtube_link")

        uploaded_file = request.files.get("file")

        file_path = None
        file_type = None

        if uploaded_file and uploaded_file.filename != "":

            file_path = save_uploaded_file(
                uploaded_file
            )

            if file_path:
                file_type = (
                    uploaded_file.filename
                    .rsplit('.', 1)[1]
                    .lower()
                )

        query = """
        INSERT INTO materials
        (
            title,
            description,
            file_path,
            file_type,
            youtube_link,
            uploaded_by,
            subject_id,
            semester,
            year
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            title,
            description,
            file_path,
            file_type,
            youtube_link,
            session['user_id'],
            subject_id,
            semester,
            year
        )

        cursor.execute(query, values)
        conn.commit()

        flash(
            "Material uploaded successfully.",
            "success"
        )

        return redirect(
            url_for('dashboard')
        )

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY semester
    """)

    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "upload_material.html",
        subjects=subjects
    )


# -----------------------------
# SEARCH
# -----------------------------

@app.route('/search')
@login_required
def search():

    keyword = request.args.get(
        'keyword',
        ''
    )

    semester = request.args.get(
        'semester',
        ''
    )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT
        m.*,
        s.subject_name,
        u.name AS uploader
    FROM materials m
    JOIN subjects s
        ON m.subject_id=s.subject_id
    JOIN users u
        ON m.uploaded_by=u.user_id
    WHERE 1=1
    """

    params = []

    if keyword:

        query += """
        AND
        (
            m.title LIKE %s
            OR s.subject_name LIKE %s
            OR u.name LIKE %s
        )
        """

        keyword_value = f"%{keyword}%"

        params.extend([
            keyword_value,
            keyword_value,
            keyword_value
        ])

    if semester:

        query += """
        AND m.semester=%s
        """

        params.append(semester)

    query += """
    ORDER BY m.upload_date DESC
    """

    cursor.execute(
        query,
        tuple(params)
    )

    materials = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "search_results.html",
        materials=materials
    )


# -----------------------------
# MATERIAL DETAILS
# -----------------------------

@app.route('/material/<int:material_id>')
@login_required
def material_details(material_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            m.*,
            s.subject_name,
            u.name AS uploader
        FROM materials m
        JOIN subjects s
            ON m.subject_id=s.subject_id
        JOIN users u
            ON m.uploaded_by=u.user_id
        WHERE m.material_id=%s
    """, (material_id,))

    material = cursor.fetchone()

    cursor.execute("""
        SELECT
            r.*,
            u.name
        FROM ratings r
        JOIN users u
            ON r.user_id=u.user_id
        WHERE material_id=%s
        ORDER BY r.created_at DESC
    """, (material_id,))

    comments = cursor.fetchall()

    cursor.execute("""
        SELECT
            ROUND(AVG(rating),1)
            AS average_rating
        FROM ratings
        WHERE material_id=%s
    """, (material_id,))

    avg_rating = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "material_details.html",
        material=material,
        comments=comments,
        avg_rating=avg_rating
    )


# -----------------------------
# DOWNLOAD FILE
# -----------------------------

@app.route('/download/<path:filename>')
@login_required
def download_file(filename):

    folder = os.path.dirname(filename)

    file_name = os.path.basename(filename)

    return send_from_directory(
        folder,
        file_name,
        as_attachment=True
    )


# -----------------------------
# PDF PREVIEW
# -----------------------------

@app.route('/preview/<int:material_id>')
@login_required
def preview_pdf(material_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM materials
        WHERE material_id=%s
    """, (material_id,))

    material = cursor.fetchone()

    cursor.close()
    conn.close()

    if not material:
        flash(
            "Material not found.",
            "danger"
        )

        return redirect(
            url_for('dashboard')
        )

    if material['file_type'] != 'pdf':

        flash(
            "Preview available only for PDFs.",
            "warning"
        )

        return redirect(
            url_for(
                'material_details',
                material_id=material_id
            )
        )

    directory = os.path.dirname(
        material['file_path']
    )

    filename = os.path.basename(
        material['file_path']
    )

    return send_from_directory(
        directory,
        filename
    )


# -----------------------------
# BOOKMARKS
# -----------------------------

@app.route('/add_bookmark/<int:material_id>')
@login_required
def add_bookmark(material_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookmarks
        (user_id, material_id)
        VALUES (%s,%s)
    """, (
        session['user_id'],
        material_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Material bookmarked successfully.",
        "success"
    )

    return redirect(
        url_for(
            'material_details',
            material_id=material_id
        )
    )


@app.route('/bookmarks')
@login_required
def bookmarks():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            m.*,
            s.subject_name
        FROM bookmarks b
        JOIN materials m
            ON b.material_id=m.material_id
        JOIN subjects s
            ON m.subject_id=s.subject_id
        WHERE b.user_id=%s
    """, (
        session['user_id'],
    ))

    materials = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "bookmarks.html",
        materials=materials
    )


# -----------------------------
# RATINGS & COMMENTS
# -----------------------------

@app.route(
    '/rate_material/<int:material_id>',
    methods=['POST']
)
@login_required
def rate_material(material_id):

    rating = request.form.get('rating')
    comment = request.form.get('comment')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ratings
        (
            material_id,
            user_id,
            rating,
            comment
        )
        VALUES (%s,%s,%s,%s)
    """, (
        material_id,
        session['user_id'],
        rating,
        comment
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Thank you for your feedback.",
        "success"
    )

    return redirect(
        url_for(
            'material_details',
            material_id=material_id
        )
    )


# -----------------------------
# REQUESTS PAGE
# -----------------------------

@app.route('/requests')
@login_required
def requests_page():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.*,
            s.subject_name,
            u.name AS requester
        FROM requests r
        JOIN subjects s
            ON r.subject_id=s.subject_id
        JOIN users u
            ON r.requested_by=u.user_id
        ORDER BY r.created_at DESC
    """)
    requests_data = cursor.fetchall()

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY semester
    """)
    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "requests.html",
        requests=requests_data,
        subjects=subjects
    )


# -----------------------------
# CREATE REQUEST
# -----------------------------

@app.route(
    '/create_request',
    methods=['GET', 'POST']
)
@login_required
def create_request():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        title = request.form.get('title')
        description = request.form.get(
            'description'
        )
        subject_id = request.form.get(
            'subject_id'
        )

        cursor.execute("""
            INSERT INTO requests
            (
                title,
                description,
                subject_id,
                requested_by
            )
            VALUES (%s,%s,%s,%s)
        """, (
            title,
            description,
            subject_id,
            session['user_id']
        ))

        conn.commit()

        flash(
            "Request posted successfully.",
            "success"
        )

        return redirect(
            url_for('requests_page')
        )

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY semester
    """)

    subjects = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "requests.html",
        subjects=subjects
    )


# -----------------------------
# ACCEPT REQUEST
# -----------------------------

@app.route(
    '/accept_request/<int:request_id>'
)
@login_required
def accept_request(request_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE requests
        SET
            assigned_to=%s,
            status='Accepted'
        WHERE request_id=%s
    """, (
        session['user_id'],
        request_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Request accepted.",
        "success"
    )

    return redirect(
        url_for('requests_page')
    )


# -----------------------------
# FULFILL REQUEST
# -----------------------------

@app.route(
    '/fulfill_request/<int:request_id>',
    methods=['POST']
)
@login_required
def fulfill_request(request_id):

    material_id = request.form.get(
        'material_id'
    )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE requests
        SET status='Fulfilled'
        WHERE request_id=%s
    """, (
        request_id,
    ))

    cursor.execute("""
        INSERT INTO request_fulfillment
        (
            request_id,
            material_id,
            fulfilled_by
        )
        VALUES (%s,%s,%s)
    """, (
        request_id,
        material_id,
        session['user_id']
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Request fulfilled successfully.",
        "success"
    )

    return redirect(
        url_for('requests_page')
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == '__main__':

    app.run(
        debug=True
    )