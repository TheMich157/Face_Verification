import cv2
import face_recognition
import numpy as np
from PIL import Image
import io
import logging
from datetime import datetime

logger = logging.getLogger('age-verify-bot')

class FaceDetector:
    def __init__(self):
        self.age_ranges = {
            'child': {'ratio_range': (0.75, 0.85), 'estimated_age': 10},
            'teen': {'ratio_range': (0.85, 0.95), 'estimated_age': 15},
            'adult': {'ratio_range': (0.95, 1.1), 'estimated_age': 20}
        }
        self.min_face_size = (30, 30)
        self.last_processed = {}

    def _calculate_face_features(self, face_landmarks):
        """Calculate facial features for age estimation"""
        try:
            # Get key facial landmarks
            nose = np.mean(face_landmarks['nose_bridge'], axis=0)
            left_eye = np.mean(face_landmarks['left_eye'], axis=0)
            right_eye = np.mean(face_landmarks['right_eye'], axis=0)
            top_lip = np.mean(face_landmarks['top_lip'], axis=0)
            bottom_lip = np.mean(face_landmarks['bottom_lip'], axis=0)
            
            # Calculate ratios that correlate with age
            eye_distance = np.linalg.norm(left_eye - right_eye)
            face_height = np.linalg.norm(nose - np.mean([top_lip, bottom_lip], axis=0))
            face_ratio = eye_distance / face_height if face_height > 0 else 0
            
            return face_ratio
        except Exception as e:
            logger.error(f"Error calculating face features: {e}")
            return None

    def _estimate_age_from_ratio(self, ratio):
        """Estimate age based on facial proportions"""
        if ratio is None:
            return None

        # Default to adult if ratio is unclear
        estimated_age = 20

        for age_group, params in self.age_ranges.items():
            min_ratio, max_ratio = params['ratio_range']
            if min_ratio <= ratio <= max_ratio:
                estimated_age = params['estimated_age']
                break

        return estimated_age

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

            # Convert to RGB for face_recognition
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return None, "No face detected in the image"

            # Get facial landmarks
            face_landmarks_list = face_recognition.face_landmarks(rgb_img, face_locations)
            if not face_landmarks_list:
                return None, "Could not detect facial features"

            # Calculate facial features and estimate age
            face_ratio = self._calculate_face_features(face_landmarks_list[0])
            estimated_age = self._estimate_age_from_ratio(face_ratio)

            if estimated_age is None:
                return None, "Could not estimate age from facial features"

            return estimated_age, None

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None, f"Error processing image: {str(e)}"

    def process_video(self, video_data):
        """Process video data and estimate age"""
        try:
            # Save video data to temporary buffer
            video_buffer = io.BytesIO(video_data)
            
            # Open video file
            cap = cv2.VideoCapture(video_buffer.name)
            
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
                    # Convert to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces
                    face_locations = face_recognition.face_locations(rgb_frame)
                    if face_locations:
                        face_landmarks_list = face_recognition.face_landmarks(rgb_frame, face_locations)
                        if face_landmarks_list:
                            face_ratio = self._calculate_face_features(face_landmarks_list[0])
                            estimated_age = self._estimate_age_from_ratio(face_ratio)
                            if estimated_age is not None:
                                age_estimates.append(estimated_age)

                frame_count += 1

            cap.release()

            if not age_estimates:
                return None, "No faces detected in video"

            # Return median age estimation
            median_age = float(np.median(age_estimates))
            return median_age, None

        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None, f"Error processing video: {str(e)}"

    def is_spoof(self, image_data):
        """Check for potential spoofing attempts"""
        try:
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return True, "Failed to load image"

            # Convert to RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Basic quality checks
            blur_score = cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
            if blur_score < 100:
                return True, "Image too blurry - possible printed photo"

            # Check face detection consistency
            face_locations = face_recognition.face_locations(rgb_img)
            if not face_locations:
                return True, "No face detected"
            
            if len(face_locations) > 1:
                return True, "Multiple faces detected"

            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            if not face_encodings:
                return True, "Cannot extract facial features"

            return False, None

        except Exception as e:
            logger.error(f"Error in spoof detection: {e}")
            return True, f"Error in spoof detection: {str(e)}"
