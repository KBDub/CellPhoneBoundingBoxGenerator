import cv2
import torch
from ultralytics import YOLO
import os
import tempfile
import uuid

class VideoProcessor:
    # COCO class names that we want to detect
    SUPPORTED_CLASSES = {
        67: 'cell phone',
        73: 'laptop',
        72: 'tv',
        63: 'laptop',
        62: 'chair',
        64: 'mouse',
        66: 'keyboard',
        28: 'suitcase',
        39: 'bottle'
    }

    def __init__(self, video_path, target_classes=None):
        self.video_path = video_path
        # Load YOLO model
        self.model = YOLO('yolov8n.pt')
        self.temp_dir = tempfile.gettempdir()
        self.target_classes = target_classes if target_classes else list(self.SUPPORTED_CLASSES.keys())

    def process(self):
        """Process video and return paths to extracted object images"""
        cap = cv2.VideoCapture(self.video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        extracted_images = []

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame with YOLO
            results = self.model(frame)
            
            # Filter for target class detections
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls)
                    if class_id in self.target_classes:
                        # Extract coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Extract object image
                        obj_img = frame[y1:y2, x1:x2]
                        
                        # Save extracted image
                        class_name = self.SUPPORTED_CLASSES[class_id]
                        img_filename = f"{class_name.replace(' ', '_')}_{uuid.uuid4()}.jpg"
                        img_path = os.path.join(self.temp_dir, img_filename)
                        cv2.imwrite(img_path, obj_img)
                        # Include class name with the image path
                        extracted_images.append({
                            'path': img_path,
                            'class': class_name
                        })

            frame_idx += 1

        cap.release()
        return extracted_images

    @classmethod
    def get_supported_classes(cls):
        """Return dictionary of supported classes"""
        return cls.SUPPORTED_CLASSES
