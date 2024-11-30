import os
import tempfile
import time
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

@app.route('/classes')
def get_classes():
    return jsonify(VideoProcessor.get_supported_classes())

@app.route('/upload', methods=['POST'])
def upload_file():
    # Clean up old files before processing new upload
    cleanup_old_files()
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

        # Get selected classes from form data
        selected_classes = request.form.getlist('classes[]')
        selected_classes = [int(cls) for cls in selected_classes] if selected_classes else None
        
        # Process video
        processor = VideoProcessor(filepath, target_classes=selected_classes)
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
        # Remove 'tmp/' prefix if present
        clean_path = image_path.replace('tmp/', '', 1)
        # Get full path in temp directory
        full_path = os.path.join(tempfile.gettempdir(), os.path.basename(clean_path))
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File not found'}), 404

        # Verify file is a valid image
        try:
            import imghdr
            with open(full_path, 'rb') as f:
                image_type = imghdr.what(f)
            if not image_type:
                return jsonify({'error': 'Invalid image file'}), 400
        except Exception:
            return jsonify({'error': 'Unable to verify image integrity'}), 400
            
        response = send_file(
            full_path,
            mimetype=f'image/{image_type}',
            as_attachment=False,
            max_age=3600  # 1 hour cache
        )
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def cleanup_old_files():
    """Clean up old temporary files (older than 1 hour)"""
    temp_dir = tempfile.gettempdir()
    current_time = time.time()
    max_age = 3600  # 1 hour
    
    for filename in os.listdir(temp_dir):
        if filename.endswith('.jpg'):  # Only process our image files
            filepath = os.path.join(temp_dir, filename)
            try:
                if current_time - os.path.getctime(filepath) > max_age:
                    os.remove(filepath)
            except OSError:
                continue
