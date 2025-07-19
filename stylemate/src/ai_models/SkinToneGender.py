# SkinToneGender.py

import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import matplotlib.pyplot as plt
import io
from PIL import Image
import tempfile # For temporary file handling

# For Google Colab compatibility
try:
    from google.colab.patches import cv2_imshow
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# Import Roboflow client
try:
    from inference_sdk import InferenceHTTPClient
    ROBOFLOW_AVAILABLE = True
except ImportError:
    print("Warning: inference_sdk not found. Gender detection will be skipped.")
    print("Install using: pip install inference_sdk")
    ROBOFLOW_AVAILABLE = False

class SkinToneClassifier:
    """Classifies skin tones (lightness and undertone) and provides recommendations"""

    LIGHTNESS_CATEGORIES = {
        'Fair': (204, 255), 'Light': (179, 203), 'Medium': (153, 178),
        'Tan': (128, 152), 'Brown': (102, 127), 'Dark': (0, 101)
    }

    COLOR_RECOMMENDATIONS = {
        'Fair Warm': {'best': ['Peach', 'Coral', 'Gold', 'Cream', 'Olive', 'Brown', 'Khaki', 'Tan', 'Orange'], 
                      'avoid': ['Silver', 'Grey', 'Black', 'Navy', 'Magenta', 'Purple']},
        'Fair Cool': {'best': ['Lavender', 'Pink', 'Blue', 'Teal', 'Silver', 'Grey', 'Navy', 'Purple', 'Red'],
                      'avoid': ['Gold', 'Orange', 'Mustard', 'Olive', 'Brown', 'Khaki', 'Beige']},
        'Fair Neutral': {'best': ['Ivory', 'Off_White', 'Beige', 'Grey', 'Teal', 'Red', 'Navy', 'Green', 'Pink'],
                      'avoid': ['Mustard', 'Olive', 'Orange']},
        'Light Warm': {'best': ['Peach', 'Coral', 'Gold', 'Cream', 'Olive', 'Khaki', 'Tan', 'Beige', 'Mustard'],
                      'avoid': ['Silver', 'Grey', 'Magenta', 'Blue', 'Purple']},
        'Light Cool': {'best': ['Lavender', 'Pink', 'Blue', 'Teal', 'Silver', 'Grey', 'Navy', 'Purple', 'Green'],
                      'avoid': ['Gold', 'Orange', 'Mustard', 'Olive', 'Brown', 'Khaki']},
        'Light Neutral': {'best': ['Ivory', 'Off_White', 'Beige', 'Grey', 'Teal', 'Red', 'Navy', 'Green', 'Pink', 'Blue'],
                          'avoid': ['Mustard', 'Olive']},
        'Medium Warm': {'best': ['Olive', 'Mustard', 'Gold', 'Brown', 'Coral', 'Red', 'Teal', 'Khaki', 'Orange'],
                        'avoid': ['Silver', 'Blue', 'Lavender', 'Grey', 'Pink']},
        'Medium Cool': {'best': ['Red', 'Purple', 'Navy', 'Green', 'Teal', 'Magenta', 'Grey', 'Silver', 'Blue'],
                        'avoid': ['Gold', 'Orange', 'Mustard', 'Olive', 'Brown', 'Beige', 'Cream']},
        'Medium Neutral': {'best': ['Red', 'Green', 'Purple', 'Teal', 'Navy', 'Brown', 'Olive', 'Mustard', 'Grey'], 
                           'avoid': ['Lavender', 'Pink', 'Peach']},
        'Tan Warm': {'best': ['Olive', 'Mustard', 'Gold', 'Brown', 'Coral', 'Red', 'Khaki', 'Tan', 'Orange'], 
                     'avoid': ['Silver', 'Blue', 'Lavender', 'Grey', 'Pink']},
        'Tan Cool': {'best': ['Red', 'Purple', 'Navy', 'Green', 'Teal', 'Magenta', 'Grey', 'Silver', 'Blue', 'Maroon'],
                     'avoid': ['Gold', 'Orange', 'Mustard', 'Olive', 'Brown', 'Beige', 'Cream']},
        'Tan Neutral': {'best': ['Olive', 'Mustard', 'Gold', 'Brown', 'Coral', 'Red', 'Teal', 'Khaki', 'Purple', 'Navy'],
                        'avoid': ['Lavender', 'Pink']},
        'Brown Warm': {'best': ['Gold', 'Brown', 'Red', 'Maroon', 'Olive', 'Mustard', 'Orange', 'Coral', 'Khaki'],
                       'avoid': ['Silver', 'Blue', 'Grey', 'Lavender', 'Pink']},
        'Brown Cool': {'best': ['Red', 'Purple', 'Navy', 'Green', 'Teal', 'Magenta', 'Silver', 'Blue', 'Maroon', 'Black'],
                       'avoid': ['Gold', 'Orange', 'Mustard', 'Beige', 'Cream', 'Yellow']},
        'Brown Neutral': {'best': ['Gold', 'Brown', 'Red', 'Maroon', 'Green', 'Blue', 'Purple', 'Teal', 'Navy', 'Black'],
                          'avoid': ['Grey', 'Beige']},
        'Dark Warm': {'best': ['Gold', 'Red', 'Orange', 'Brown', 'Olive', 'Mustard', 'Coral', 'Maroon', 'Yellow'],
                      'avoid': ['Silver', 'Blue', 'Grey', 'Lavender', 'Pink', 'White']},
        'Dark Cool': {'best': ['Red', 'Purple', 'Navy', 'Green', 'Teal', 'Magenta', 'Silver', 'Blue', 'Black', 'White'],
                      'avoid': ['Gold', 'Orange', 'Mustard', 'Olive', 'Beige', 'Cream', 'Brown']},
        'Dark Neutral': {'best': ['Red', 'Blue', 'Green', 'Purple', 'Gold', 'White', 'Black', 'Magenta', 'Violet', 'Maroon'], 
                         'avoid': ['Beige', 'Khaki']},
        'Undefined': {'best': ['Navy', 'Teal', 'Grey', 'White', 'Maroon', 'Olive', 'Mustard', 'Charcoal'],
                      'avoid': ['Lime', 'Orange', 'Yellow']}
    }

    @staticmethod
    def classify_undertone(a, b):
        T_warm = 2; T_cool = 1
        if b > a + T_warm: return 'Warm'
        elif a > b + T_cool: return 'Cool'
        else: return 'Neutral'

    @staticmethod
    def classify_skin(rgb_color):
        lab_color = cv2.cvtColor(np.array([[rgb_color]], dtype=np.uint8), cv2.COLOR_RGB2LAB)[0][0]
        L, a, b = lab_color
        lightness_category = 'Undefined'
        for category, (min_val, max_val) in SkinToneClassifier.LIGHTNESS_CATEGORIES.items():
            if min_val <= L <= max_val: lightness_category = category; break
        if lightness_category == 'Undefined': combined_name = 'Undefined'
        else: undertone = SkinToneClassifier.classify_undertone(a, b); combined_name = f"{lightness_category} {undertone}"
        return combined_name

    @staticmethod
    def get_recommendations(combined_skin_tone):
        return SkinToneClassifier.COLOR_RECOMMENDATIONS.get(combined_skin_tone, SkinToneClassifier.COLOR_RECOMMENDATIONS['Undefined'])


class FaceDetector:
    def __init__(self, model_path):
        self.model_path = model_path
        try:
            self.detector = cv2.FaceDetectorYN_create(model_path, "", (320, 320), 0.85, 0.3, 5000)
            self.model_loaded = True
        except Exception as e: print(f"Error loading face detection model: {str(e)}"); self.model_loaded = False
    def detect_faces(self, image):
        if not self.model_loaded: return np.array([])
        h, w = image.shape[:2]; self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(image)
        return faces if faces is not None else np.array([])

class SkinAnalyzer:
    @staticmethod
    def get_skin_mask(face_roi):
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV); ycrcb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2YCrCb)
        lower_hsv = np.array([0, 30, 60], dtype=np.uint8); upper_hsv = np.array([25, 255, 255], dtype=np.uint8)
        lower_ycrcb = np.array([0, 135, 85], dtype=np.uint8); upper_ycrcb = np.array([255, 180, 135], dtype=np.uint8)
        hsv_mask = cv2.inRange(hsv, lower_hsv, upper_hsv); ycrcb_mask = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)
        combined_mask = cv2.bitwise_and(hsv_mask, ycrcb_mask)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        return cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    @staticmethod
    def get_dominant_color(roi, mask):
        masked_pixels = roi[mask == 255]
        if len(masked_pixels) < 50: return None
        kmeans = KMeans(n_clusters=3, n_init=10); kmeans.fit(masked_pixels)
        counts = np.bincount(kmeans.labels_); dominant_idx = np.argmax(counts)
        return kmeans.cluster_centers_[dominant_idx].astype(int)

class GenderDetector:
    """Detects gender using Roboflow Inference API"""
    def __init__(self, api_key, model_id="gender-detection-qiyyg/2"):
        self.api_key = api_key
        self.model_id = model_id
        if ROBOFLOW_AVAILABLE:
            try:
                self.client = InferenceHTTPClient(api_url="https://detect.roboflow.com", api_key=self.api_key )
                self.client_initialized = True
            except Exception as e:
                print(f"Error initializing Roboflow client: {e}")
                self.client_initialized = False
        else:
            self.client_initialized = False

    def detect_gender(self, face_roi):
        """Detect gender from a face ROI"""
        if not self.client_initialized:
            return "Unknown", 0.0

        # Save face ROI to a temporary file
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                temp_file_path = tf.name
                cv2.imwrite(temp_file_path, face_roi)

            # Perform inference
            result = self.client.infer(temp_file_path, model_id=self.model_id)

            # Process result
            if 'predictions' in result and result['predictions']:
                prediction = result['predictions'][0]
                gender = prediction['class']
                confidence = prediction['confidence']
                return gender, confidence
            else:
                return "Unknown", 0.0

        except Exception as e:
            print(f"Error during gender detection API call: {e}")
            return "Error", 0.0
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)

class Visualizer:
    @staticmethod
    def create_visualization(original_img, face_roi, skin_mask, dominant_bgr_color, combined_skin_tone, hex_color, gender_label):
        rgb_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
        face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
        skin_rgb = cv2.cvtColor(skin_mask, cv2.COLOR_GRAY2RGB)
        color_swatch = np.ones((200, 200, 3), dtype=np.uint8); color_swatch[:] = dominant_bgr_color
        plt.figure(figsize=(16, 5))
        plt.subplot(1, 4, 1); plt.imshow(rgb_img); plt.title('Original Image'); plt.axis('off')
        plt.subplot(1, 4, 2); plt.imshow(face_rgb); plt.title(f'Detected Face\n{gender_label}'); plt.axis('off') # Add gender label
        plt.subplot(1, 4, 3); overlay = cv2.addWeighted(face_rgb, 0.7, skin_rgb, 0.3, 0); plt.imshow(overlay); plt.title('Skin Detection'); plt.axis('off')
        plt.subplot(1, 4, 4); plt.imshow(cv2.cvtColor(color_swatch, cv2.COLOR_BGR2RGB)); plt.title(f'{combined_skin_tone}\n{hex_color}'); plt.axis('off')
        plt.tight_layout()
        buf = io.BytesIO(); plt.savefig(buf, format='png'); buf.seek(0)
        img = Image.open(buf); viz_image = np.array(img); viz_image = cv2.cvtColor(viz_image, cv2.COLOR_RGB2BGR)
        plt.close()
        return viz_image
    @staticmethod
    def display_visualization(viz_image):
        if IN_COLAB: cv2_imshow(viz_image)
        else: pass # Removed cv2.imshow to prevent pop-up

class FashionAssistantPipeline:
    """Main class for combined skin tone and gender detection pipeline"""
    def __init__(self, face_model_path, gender_api_key):
        self.face_detector = FaceDetector(face_model_path)
        self.skin_analyzer = SkinAnalyzer()
        self.visualizer = Visualizer()
        self.gender_detector = GenderDetector(gender_api_key)

    def analyze_image(self, image_data, generate_visualization=False):
        try:
            if isinstance(image_data, str):
                img = cv2.imread(image_data)
                if img is None: return {"error": "Failed to load image"}
            else: img = image_data.copy()
            if img is None or img.size == 0: return {"error": "Invalid image"}

            faces = self.face_detector.detect_faces(img)
            if faces.size == 0: return {"error": "No faces detected"}

            # --- Process the first detected face ---
            x, y, w, h = map(int, faces[0][:4])
            face_roi = img[y:y+h, x:x+w]
            if face_roi.size == 0 or face_roi.shape[0] < 20 or face_roi.shape[1] < 20: return {"error": "Invalid face region"}

            # Skin Tone Analysis
            skin_mask = self.skin_analyzer.get_skin_mask(face_roi)
            dominant_bgr_color = self.skin_analyzer.get_dominant_color(face_roi, skin_mask)
            if dominant_bgr_color is None: return {"error": "No skin detected"}
            b, g, r = dominant_bgr_color; rgb_color = (r, g, b)
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            combined_category = SkinToneClassifier.classify_skin(rgb_color)
            recommendations = SkinToneClassifier.get_recommendations(combined_category)

            # Gender Detection
            gender, gender_confidence = self.gender_detector.detect_gender(face_roi)
            gender_label = f"{gender} ({gender_confidence:.2f})" if gender not in ["Unknown", "Error"] else gender

            result = {
                "success": True,
                "skin_tone": combined_category,
                "gender": gender,
                "gender_confidence": gender_confidence,
                "rgb_color": rgb_color,
                "hex_color": hex_color.upper(),
                "recommendations": recommendations,
                "coordinates": {"face": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}}
            }

            if generate_visualization:
                viz_image = self.visualizer.create_visualization(img, face_roi, skin_mask, dominant_bgr_color, combined_category, hex_color.upper(), gender_label)
                result["visualization"] = viz_image
                annotated_img = img.copy(); cv2.rectangle(annotated_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(annotated_img, gender_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2) # Add gender label to annotated image
                result["annotated_image"] = annotated_img

            return result
        except Exception as e: return {"error": f"Processing error: {str(e)}"}

    def save_visualization(self, result, output_path):
        if "error" in result or "visualization" not in result: return False
        cv2.imwrite(output_path, result["visualization"]); return True

    def display_results(self, result):
        if "error" in result: print(f"Error: {result['error']}"); return False
        print(f"  Skin Tone: {result['skin_tone']}")
        print(f"  Detected Gender: {result['gender']} (Confidence: {result['gender_confidence']:.2f})")
        print(f"  Dominant Color (Hex): {result['hex_color']}")
        print(f"  Recommendations for {result['skin_tone']}:")
        print(f"    Best colors to wear: {', '.join(result['recommendations']['best'])}")
        print(f"    Avoid: {', '.join(result['recommendations']['avoid'])}")
        if "visualization" in result: self.visualizer.display_visualization(result["visualization"])
        return True



