import os
from flask import Flask, render_template, request
import cv2
from datetime import datetime
from werkzeug.utils import secure_filename
import mysql.connector

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# MySQL Config (apne credentials dalna)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',         # apna MySQL user
    'password': 'Ayush@123', # apna MySQL password
    'database': 'image_sketch_db'
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_sketch(img_path, output_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
    inverted_blur = 255 - blurred
    sketch = cv2.divide(gray, inverted_blur, scale=256.0)
    cv2.imwrite(output_path, sketch)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            time_stamp = datetime.now().strftime("%Y%m%d%H%M%S")
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{time_stamp}_{filename}")
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{time_stamp}_sketch_{filename}")

            # Save & convert
            file.save(input_path)
            convert_to_sketch(input_path, output_path)

            # Save in DB
            conn = connect_db()
            cursor = conn.cursor()
            sql = "INSERT INTO images (original_path, sketch_path) VALUES (%s, %s)"
            cursor.execute(sql, (input_path, output_path))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template("index.html", original=input_path, sketch=output_path)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
