import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.video_processor import VideoProcessor
import uuid

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Generate unique filename
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process video
        processor = VideoProcessor(filepath)
        result_images = processor.process()

        # Clean up
        os.remove(filepath)

        return jsonify({
            'status': 'success',
            'message': 'Video processed successfully',
            'images': result_images
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<path:image_path>')
def download_image(image_path):
    try:
        return send_file(image_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
