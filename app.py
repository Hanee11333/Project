import os
import uuid
from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64
from utils.detector import VehicleDetector

app = Flask(__name__)
app.secret_key = 'vehicle_detection_secret_key'

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Initialize the detector
detector = VehicleDetector()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    result_image = None
    vehicle_count = 0
    
    if request.method == 'POST':
        # Check if a file was submitted
        if 'image' not in request.files:
            error = 'No file part'
            return render_template('index.html', error=error)
            
        file = request.files['image']
        
        # Check if file is empty
        if file.filename == '':
            error = 'No selected file'
            return render_template('index.html', error=error)
            
        # Check if file has allowed extension
        if not allowed_file(file.filename):
            error = 'File format not supported. Please upload a .jpg, .jpeg or .png file.'
            return render_template('index.html', error=error)
            
        try:
            # Save the file with a secure name
            filename = secure_filename(file.filename)
            # Add a unique ID to avoid filename conflicts
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Process the image
            result_img, vehicle_count = detector.detect_vehicles(file_path)
            
            # Save the result image
            result_filename = f"result_{unique_filename}"
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], result_filename)
            result_img.save(result_path)
            
            # Create URL for the result image
            result_image = url_for('static', filename=result_filename)
            
        except Exception as e:
            error = f"Error processing image: {str(e)}"
            
    return render_template('index.html', error=error, result_image=result_image, vehicle_count=vehicle_count)

@app.route('/technical')
def technical():
    return render_template('technical.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 