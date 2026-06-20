import os

class Config:
    SECRET_KEY = "syllabuzz_secret_key"

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "sam123"
    MYSQL_DATABASE = "syllabuzz"

    UPLOAD_FOLDER = "uploads"

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "ppt",
        "pptx",
        "jpg",
        "jpeg",
        "png",
        "gif"
    }

    PDF_FOLDER = os.path.join(UPLOAD_FOLDER, "pdfs")
    DOC_FOLDER = os.path.join(UPLOAD_FOLDER, "docs")
    PPT_FOLDER = os.path.join(UPLOAD_FOLDER, "ppts")
    IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")


    VVCE_EMAIL_DOMAIN = "@vvce.ac.in"