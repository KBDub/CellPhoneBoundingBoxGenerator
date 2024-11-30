import cv2
import torch
from ultralytics import YOLO
import os
import tempfile
import uuid

class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        # Load YOLO model
        self.model = YOLO('yolov8n.pt')
        self.temp_dir = tempfile.gettempdir()

    def process(self):
        """Process video and return paths to extracted phone images"""
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
            
            # Filter for cell phone detections (class 67 in COCO dataset)
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    if int(box.cls) == 67:  # Cell phone class
                        # Extract coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Extract phone image
                        phone_img = frame[y1:y2, x1:x2]
                        
                        # Save extracted image
                        img_filename = f"phone_{uuid.uuid4()}.jpg"
                        img_path = os.path.join(self.temp_dir, img_filename)
                        cv2.imwrite(img_path, phone_img)
                        extracted_images.append(img_path)

            frame_idx += 1

        cap.release()
        return extracted_images
