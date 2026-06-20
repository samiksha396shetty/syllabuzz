# SYLLABUZZ

SYLLABUZZ is a study material sharing platform designed for students and professors. It provides a centralized place to upload, search, download, bookmark, and rate academic resources such as notes, PDFs, presentations, images, and educational video links.

The platform also includes a request system where students can request materials that are not available and track their fulfillment status.

---

## Features

### User Management
- Student and Professor Registration
- Secure Login and Logout
- Password Hashing for Security
- VVCE Email Verification

### Study Material Sharing
- Upload Notes and Resources
- Support for:
  - PDF Files
  - DOC/DOCX Files
  - PPT/PPTX Files
  - Images
  - YouTube Links
- Download Uploaded Materials
- PDF Preview Support

### Search System
- Search by Material Title
- Search by Subject
- Search by Uploader
- Filter by Semester

### Bookmarks
- Save Important Materials
- Access Saved Materials Anytime

### Ratings and Feedback
- Rate Materials from 1–10
- Add Comments and Reviews
- View Average Ratings

### Material Request System
- Request Missing Study Materials
- Accept Requests
- Mark Requests as Fulfilled
- Track Request Status

### Dashboard
- Total Students
- Total Professors
- Total Materials
- Total Requests
- Recently Uploaded Materials

---

## Technology Stack

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Backend
- Python
- Flask

### Database
- MySQL

### Additional Libraries
- mysql-connector-python
- Werkzeug

---

## Database Tables

The project uses the following tables:

1. users
2. subjects
3. materials
4. ratings
5. bookmarks
6. requests
7. request_fulfillment

---

## Folder Structure

```
SYLLABUZZ/
│
├── app.py
├── config.py
├── requirements.txt
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload_material.html
│   ├── material_details.html
│   ├── bookmarks.html
│   ├── requests.html
│   └── search_results.html
│
├── uploads/
│   ├── pdfs/
│   ├── docs/
│   ├── ppts/
│   └── images/
│
└── static/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/samiksha396shetty/syllabuzz.git
```

### Open Project

```bash
cd syllabuzz
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure MySQL

Create a database named:

```sql
CREATE DATABASE syllabuzz;
```

Import the required tables.

Update database credentials inside:

```python
config.py
```

### Run Project

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000
```

---

## Future Improvements

- AI-based Material Recommendations
- Material Verification System
- Advanced Search Filters
- Notifications for Request Updates
- Mobile Responsive Design
- Cloud Storage Integration

---

## Developed By

Samiksha Shetty

Academic Project – SYLLABUZZ
