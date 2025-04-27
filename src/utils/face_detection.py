import cv2
import dlib
import numpy as np
from PIL import Image
import io

class FaceDetector:
    def __init__(self):
        # Initialize dlib's face detector and facial landmarks predictor
        self.detector = dlib.get_frontal_face_detector()
        
        # Parameters for age estimation based on facial features
        self.age_ranges = {
            'child': {'ratio_range': (0.75, 0.85), 'estimated_age': 10},
            'teen': {'ratio_range': (0.85, 0.95), 'estimated_age': 15},
            'adult': {'ratio_range': (0.95, 1.1), 'estimated_age': 20}
        }

    def _calculate_face_ratios(self, face):
        """Calculate facial ratios that correlate with age"""
        # Convert dlib rectangle to coordinates
        x, y = face.left(), face.top()
        w, h = face.width(), face.height()
        
        # Calculate face proportions (simplified age estimation)
        face_ratio = w / h
        return face_ratio

    def _estimate_age_from_ratio(self, ratio):
        """Estimate age based on facial proportions"""
        for age_group, params in self.age_ranges.items():
            min_ratio, max_ratio = params['ratio_range']
            if min_ratio <= ratio <= max_ratio:
                return params['estimated_age']
        return 20  # Default to adult if ratios are inconclusive

    def process_image(self, image_data):
        """Process image data and estimate age"""
        try:
            # Convert image data to numpy array
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = cv2.imread(image_data)

            if img is None:
                return None, "Failed to load image"

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.detector(gray)

            if not faces:
                return None, "No face detected in the image"

            # Process the first detected face
            face = faces[0]
            face_ratio = self._calculate_face_ratios(face)
            estimated_age = self._estimate_age_from_ratio(face_ratio)

            return estimated_age, None

        except Exception as e:
            return None, f"Error processing image: {str(e)}"

    def process_video(self, video_data):
        """Process video data and estimate age"""
        try:
            # Save video data to temporary file
            temp_video = io.BytesIO(video_data)
            
            # Open video file
            cap = cv2.VideoCapture(temp_video.name)
            
            if not cap.isOpened():
                return None, "Failed to open video"

            age_estimates = []
            frame_count = 0
            max_frames = 30  # Process up to 30 frames

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # Process every 5th frame
                if frame_count % 5 == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.detector(gray)

                    if faces:
                        face = faces[0]
                        face_ratio = self._calculate_face_ratios(face)
                        estimated_age = self._estimate_age_from_ratio(face_ratio)
                        age_estimates.append(estimated_age)

                frame_count += 1

            cap.release()

            if not age_estimates:
                return None, "No faces detected in video"

            # Return median age estimation
            median_age = float(np.median(age_estimates))
            return median_age, None

        except Exception as e:
            return None, f"Error processing video: {str(e)}"

    def is_spoof(self, image_data):
        """Basic anti-spoofing check"""
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return True, "Failed to load image"

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate image quality metrics
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Check if image is too blurry (potential printed photo)
            if blur_score < 100:
                return True, "Image too blurry - possible printed photo"
                
            return False, None

        except Exception as e:
            return True, f"Error in spoof detection: {str(e)}"
