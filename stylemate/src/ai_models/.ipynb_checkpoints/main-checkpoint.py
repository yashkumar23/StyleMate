
# main.py

import cv2
import mediapipe as mp
import numpy as np
import os

# Import the necessary components from SkinToneGender.py
# Note: download_yunet_model is NOT imported from SkinToneGender.py anymore
from SkinToneGender import FashionAssistantPipeline

# Ensure body_measurement_model is accessible
# Assuming body_measurement_model.py is in the same directory
from body_measurement_model import extract_keypoints, calculate_body_measurements

def main(front_view_image_path, side_view_image_path, user_height_cm, output_file_path="analysis_results.txt"):
    """
    Main function to process images, extract keypoints, calculate body measurements,
    and also perform skin tone and gender detection.

    Args:
        front_view_image_path (str): Path to the front view image.
        side_view_image_path (str): Path to the side view image.
        user_height_cm (float): User\"s actual height in centimeters.
        output_file_path (str): Path to the output text file.
    """
    # Open the output file for writing
    output_file = open(output_file_path, "w")

    # Helper function to print to console and file
    def print_and_log(*args, **kwargs):
        print(*args, **kwargs) # Print to console
        print(*args, file=output_file, **kwargs) # Print to file

    # Helper function to print only to console
    def print_to_console(*args, **kwargs):
        print(*args, **kwargs)

    try:
        print_to_console("--- Starting Body Measurement Analysis ---")
        print_to_console(f"Processing front view image for body measurements: {front_view_image_path}")
        front_results, annotated_front_image = extract_keypoints(front_view_image_path)

        print_to_console(f"Processing side view image for body measurements: {side_view_image_path}")
        side_results, annotated_side_image = extract_keypoints(side_view_image_path)

        if front_results and front_results.pose_world_landmarks:
            print_and_log("\n--- Body Measurements Results ---")
            measurements = calculate_body_measurements(front_results.pose_world_landmarks.landmark, user_height_cm)

            if measurements:
                # Print user height first
                print_and_log(f"User Height: {measurements['user_height_cm']:.2f} cm")
                for key, value in measurements.items():
                    if key != "user_height_cm": # Avoid printing user height twice
                        formatted_key = key.replace("_", " ").title()
                        print_and_log(f"{formatted_key}: {value:.2f} cm")
            else:
                print_and_log("Could not calculate body measurements. Please check the input image and ensure all required keypoints are detected.")
            print_and_log("---------------------------------")
        else:
            print_and_log("Failed to extract world landmarks from the front view image. Cannot calculate measurements.")

        # Save annotated images for visual inspection
        if annotated_front_image is not None:
            cv2.imwrite("annotated_front_view.jpg", annotated_front_image)
            print_to_console("Annotated front view image saved as annotated_front_view.jpg")
        if annotated_side_image is not None:
            cv2.imwrite("annotated_side_view.jpg", annotated_side_image)
            print_to_console("Annotated side view image saved as annotated_side_view.jpg")

        # --- Add call to Skin Tone & Gender Detection ---
        print_to_console("\n--- Starting Skin Tone & Gender Analysis ---")

        # Define the path to your pre-downloaded YuNet model
        # IMPORTANT: Ensure this path is correct and the file \'face_detection_yunet_2023mar.onnx\' exists here.
        face_model_path = "G:\stylemate_full_project_final\stylemate\src\ai_models\model_weights\face_detection_yunet_2023mar.onnx"

        if not os.path.exists(face_model_path):
            print_to_console(f"Error: YuNet face detection model not found at \'{face_model_path}\'.")
            print_to_console("Please ensure the model file is in the correct directory.")
            return # Exit if the model is not found

        # IMPORTANT: Roboflow API key provided by the user
        gender_api_key = "pIufABh634G1BkWsQWSA"

        pipeline = FashionAssistantPipeline(face_model_path, gender_api_key)

        # Analyze ONLY front view image for skin tone and gender
        print_to_console(f"\nAnalyzing front view image for skin tone and gender: {front_view_image_path}")
        front_skin_gender_result = pipeline.analyze_image(front_view_image_path, generate_visualization=True)
        print_and_log("Results for Front View Image:")
        # Redirect display_results to write to file
        if "error" in front_skin_gender_result: print_and_log(f"  Error: {front_skin_gender_result['error']}")
        else:
            print_and_log(f"  Skin Tone: {front_skin_gender_result['skin_tone']}")
            print_and_log(f"  Detected Gender: {front_skin_gender_result['gender']} (Confidence: {front_skin_gender_result['gender_confidence']:.2f})")
            print_and_log(f"  Dominant Color (Hex): {front_skin_gender_result['hex_color']}")
            print_and_log(f"  Recommendations for {front_skin_gender_result['skin_tone']}:")
            print_and_log(f"    Best colors to wear: {', '.join(front_skin_gender_result['recommendations']['best'])}")
            print_and_log(f"    Avoid: {', '.join(front_skin_gender_result['recommendations']['avoid'])}")

        if "visualization" in front_skin_gender_result:
            output_path = "front_view_skin_gender_visualization.jpg"
            if pipeline.save_visualization(front_skin_gender_result, output_path):
                print_to_console(f"Visualization saved to {output_path}")
            else:
                print_to_console("Failed to save front view visualization.")

        print_and_log("------------------------------------------")

    finally:
        output_file.close()


if __name__ == '__main__':
    # Example usage with the provided images
    front_image = "./data/0/front_img.jpg"
    side_image = "./data/0/side_img.jpg"
    # IMPORTANT: Replace with the actual user\'s height in centimeters
    user_height = 159.0  # Example height in cm

    # Check if images exist before proceeding
    if not os.path.exists(front_image):
        print(f"Error: Front image not found at {front_image}. Please ensure the path is correct.")
    if not os.path.exists(side_image):
        print(f"Error: Side image not found at {side_image}. Please ensure the path is correct.")
    if os.path.exists(front_image) and os.path.exists(side_image):
        main(front_image, side_image, user_height)
    else:
        print("Please provide valid image paths to run the analysis.")



"""# **OutFits**"""
# Cell 1: Define Functions (Updated to match analysis_results.txt structure)

import os
import re
from IPython.display import HTML, display
import os

# --- Configuration ---
dress_folder_path = "G:\stylemate_full_project_final\stylemate\src\static\Dress"
analysis_file_path = "G:\stylemate_full_project_final\stylemate\src\ai_models\analysis_results.txt"
# ----------------------

# --- Helper: Parse Analysis Results ---
def parse_analysis_output(file_path):
    import re

    gender = None
    skin_tone = None
    best_colors = []
    avoid_colors = []
    measurements = {
        "Height": None,
        "Arm Length": None,
        "Waist Circumference": None,
        "Chest Circumference": None,
        "Neck Waist Length Front": None
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if match := re.search(r"Detected Gender:\s*(\w+)", line, re.IGNORECASE):
                    gender = match.group(1).strip().capitalize()
                if match := re.search(r"Skin Tone:\s*(.+)", line, re.IGNORECASE):
                    skin_tone = match.group(1).strip()
                if match := re.search(r"(?:Best|Recommended) colors(?: to wear)?:\s*(.+)", line, re.IGNORECASE):
                    best_colors = [c.strip().lower() for c in match.group(1).split(",") if c.strip()]
                if match := re.search(r"Avoid:\s*(.+)", line, re.IGNORECASE):
                    avoid_colors = [c.strip().lower() for c in match.group(1).split(",") if c.strip()]
                if match := re.search(r"User Height:\s*([\d.]+)", line, re.IGNORECASE):
                    measurements["Height"] = match.group(1)
                if match := re.search(r"Arm Length Cm:\s*([\d.]+)", line, re.IGNORECASE):
                    measurements["Arm Length"] = match.group(1)
                if match := re.search(r"Waist Circumference Cm:\s*([\d.]+)", line, re.IGNORECASE):
                    measurements["Waist Circumference"] = match.group(1)
                if match := re.search(r"Chest Circumference Cm:\s*([\d.]+)", line, re.IGNORECASE):
                    measurements["Chest Circumference"] = match.group(1)
                if match := re.search(r"Neck Waist Length Front Cm:\s*([\d.]+)", line, re.IGNORECASE):
                    measurements["Neck Waist Length Front"] = match.group(1)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")

    return gender, skin_tone, measurements, best_colors, avoid_colors

# --- Helper: Recommend Dress Images ---
def find_recommended_dress_images(dress_base_path, gender, recommended_colors):
    import random

    if not gender or not recommended_colors:
        return []

    style_folders = []
    gender_subfolder = "Female" if gender.lower() == 'female' else "Male"
    if gender.lower() == 'female':
        style_folders = ['SAREE', 'LEHENGA', 'WOMEN_KURTA']
    else:
        style_folders = ['KURTA_MEN', 'NEHRU_JACKETS', 'SHERWANIS']

    base_gender_path = os.path.join(dress_base_path, gender_subfolder)
    selected_images_with_types = []

    for style in style_folders:
        style_path = os.path.join(base_gender_path, style)
        if not os.path.isdir(style_path):
            continue
        try:
            for color_folder in os.listdir(style_path):
                color_path = os.path.join(style_path, color_folder)
                if not os.path.isdir(color_path):
                    continue
                if color_folder.lower() in recommended_colors:
                    image_files = [
                        f for f in os.listdir(color_path)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                    ]
                    sample_images = random.sample(image_files, min(len(image_files), 2))
                    for img in sample_images:
                        selected_images_with_types.append((os.path.join(color_path, img), style))
        except Exception:
            continue

    return selected_images_with_types

# --- Validate Paths ---
if not os.path.isdir(dress_folder_path):
    print(f"Error: Dress folder not found: {dress_folder_path}")
elif not os.path.isfile(analysis_file_path):
    print(f"Error: Analysis file not found: {analysis_file_path}")
else:
    # Parse analysis output
    gender, skin_tone, measurements, best_colors, avoid_colors = parse_analysis_output(analysis_file_path)

    # --- Display Summary Info ---
    info_html = f"""
    <div style="font-family: Arial; font-size: 15px; color: #333; margin-bottom: 30px; line-height: 1.6;">
        <p><strong>👤 Gender:</strong> {gender or 'Not Found'}</p>
        <p><strong>🎨 Skin Tone:</strong> {skin_tone or 'Not Found'}</p>
        <p><strong>✅ Best Colors to Wear:</strong> {', '.join([c.capitalize() for c in best_colors]) if best_colors else 'Not Found'}</p>
        <p><strong>❌ Colors to Avoid:</strong> {', '.join([c.capitalize() for c in avoid_colors]) if avoid_colors else 'Not Found'}</p>
    </div>
    """
    display(HTML(info_html))

    # --- Find & Display Dress Recommendations ---
    images_with_types = find_recommended_dress_images(
        dress_base_path=dress_folder_path,
        gender=gender,
        recommended_colors=best_colors
    )

    if images_with_types:
        print("--- Recommended Dresses ---")
        for i, (img_path, dress_type) in enumerate(images_with_types):
            formatted_type = dress_type.replace('_', ' ').title()
            img_html = f"""
            <div style="text-align: center; margin: 30px 0;">
                <h4 style="color: #222; margin-bottom: 10px;">{formatted_type}</h4>
                <img src="{img_path}" alt="{formatted_type}" style="width:300px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            </div>
            """
            display(HTML(img_html))
    else:
        print("No recommended dresses found based on the analysis and available data.")
