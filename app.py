import os
from flask import Flask, render_template, request, send_from_directory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
UPLOAD_FOLDER = 'archive'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# AWS S3 Configuration (Reads environment variables set in Docker/EC2)
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'your-fallback-bucket-name')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

def generate_book_pdf(pdf_path, title, author):
    """Core unique function: Uses ReportLab to generate a clean Book Summary PDF."""
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "========================================")
    c.drawString(100, 730, "        CLOUD BOOK LIBRARY ARCHIVE      ")
    c.drawString(100, 710, "========================================")
    
    c.drawString(100, 650, f"Book Title: {title}")
    c.drawString(100, 620, f"Author: {author}")
    c.drawString(100, 590, "Status: Digitally Cataloged & Stored in S3")
    
    c.drawString(100, 530, "----------------------------------------")
    c.drawString(100, 500, "Thank you for using the Cloud Book Shelf system.")
    c.save()

def upload_to_aws(file_path, s3_filename):
    """Uploads the generated PDF file to AWS S3 bucket."""
    s3 = boto3.client('s3', region_name=AWS_REGION)
    try:
        s3.upload_file(file_path, S3_BUCKET, s3_filename)
        return True
    except NoCredentialsError:
        print("AWS credentials not found.")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title', 'Unknown Title')
        author = request.form.get('author', 'Unknown Author')
        file = request.files['cover']
        
        if file and file.filename != '':
            pdf_filename = f"{title.lower().replace(' ', '_')}_summary.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            
            # Run core PDF generation function
            generate_book_pdf(pdf_path, title, author)
            
            # Try uploading to S3 if bucket is configured
            if S3_BUCKET != 'your-fallback-bucket-name':
                upload_to_aws(pdf_path, f"books/{pdf_filename}")
                
            return render_template('index.html', pdf_filename=pdf_filename, title=title, author=author)
            
    return render_template('index.html')

@app.route('/archive/<filename>')
def download_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)