import os
import boto3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
S3_BUCKET = os.environ.get("S3_BUCKET", "icem-book-shelf-demo")
s3 = boto3.client("s3")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        
        # Generate unique tracking ID
        book_id = f"BOOK-{title[:3].upper()}-{os.urandom(2).hex().upper()}"
        
        # Handle file upload and S3 integration here...
        return render_template("index.html", success=True, title=title, author=author)
        
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)