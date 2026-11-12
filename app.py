
import os
import boto3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# AWS S3 Configuration (Uses IAM role credentials automatically on EC2)
S3_BUCKET = os.environ.get("S3_BUCKET", "icem-book-shelf-demo")
s3 = boto3.client("s3")

# Local fallback folder if running outside cloud/S3 mode
UPLOAD_FOLDER = "books"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    success = False
    book_title = ""
    author_name = ""
    
    if request.method == "POST":
        book_title = request.form.get("title")
        author_name = request.form.get("author")
        file = request.files.get("file")
        
        if book_title and author_name:
            # Generate unique ID (e.g., BOOK-20261112-143205-7F3A)
            book_id = f"BOOK-{os.urandom(2).hex().upper()}"
            filename = f"{book_id}.txt"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save metadata locally first
            with open(filepath, "w") as f:
                f.write(f"Title: {book_title}\nAuthor: {author_name}\n")
            
            # Try uploading to AWS S3 if bucket is configured
            try:
                s3.upload_file(filepath, S3_BUCKET, f"books/{filename}")
                print(f"Successfully uploaded {filename} to S3 bucket {S3_BUCKET}")
            except Exception as e:
                print(f"Running in local mode or S3 upload failed: {e}")
                
            success = True

    return render_template("index.html", success=success, title=book_title, author=author_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
