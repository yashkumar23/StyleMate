import os
import cv2
from src.ai_models.body_measurement_model import extract_keypoints, calculate_body_measurements
from src.ai_models.SkinToneGender import FashionAssistantPipeline




with open("analysis_results.txt", "w") as f:
    f.write("")
# Full Female Size Chart
female_size_chart = {
    "Lehnga Size Chart": {
        "Waist Circumference (cm)": {
            "S": (80.17, 82.98),
            "M": (82.98, 84.69),
            "L": (84.69, 88.00),
            "XL": (88.00, 98.17)
        }
    },
    "Saree Blouse Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.28, 90.52),
            "M": (90.52, 92.88),
            "L": (92.88, 93.92),
            "XL": (93.92, 99.51)
        }
    },
    "Women Kurta Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.28, 90.52),
            "M": (90.52, 92.88),
            "L": (92.88, 93.92),
            "XL": (93.92, 99.51)
        }
    },
    "Gown Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.28, 90.52),
            "M": (90.52, 92.88),
            "L": (92.88, 93.92),
            "XL": (93.92, 99.51)
        }
    }
}

# Full Male Size Chart
male_size_chart = {
    "Sherwani Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.64, 95.97),
            "M": (95.97, 96.96),
            "L": (96.96, 101.03),
            "XL": (101.03, 106.54)
        }
    },
    "Man Kurta Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.64, 95.97),
            "M": (95.97, 96.96),
            "L": (96.96, 101.03),
            "XL": (101.03, 106.54)
        }
    },
    "Nehru Jackets Size Chart": {
        "Chest Circumference (cm)": {
            "S": (85.64, 95.97),
            "M": (95.97, 96.96),
            "L": (96.96, 101.03),
            "XL": (101.03, 106.54)
        }
    }
}

def get_size(measurement_value, ranges):
    for size, (min_val, max_val) in ranges.items():
        if min_val <= measurement_value <= max_val:
            return size
    return "N/A"

def categorize_garments(gender, measurements):
    normalized_measurements = {}
    for k, v in measurements.items():
        k_clean = k.replace("_", " ").title()
        if k_clean.endswith("Cm"):
            k_clean = k_clean.replace("Cm", "(cm)")
        normalized_measurements[k_clean] = v

    categorized_sizes = {}
    current_chart = female_size_chart if gender.lower() == "female" else male_size_chart

    if gender.lower() == "female":
        if "Waist Circumference (cm)" in normalized_measurements:
            categorized_sizes["Lehnga"] = get_size(normalized_measurements["Waist Circumference (cm)"], current_chart["Lehnga Size Chart"]["Waist Circumference (cm)"])
        if "Chest Circumference (cm)" in normalized_measurements:
            chest = normalized_measurements["Chest Circumference (cm)"]
            categorized_sizes["Saree Blouse"] = get_size(chest, current_chart["Saree Blouse Size Chart"]["Chest Circumference (cm)"])
            categorized_sizes["Women Kurta"] = get_size(chest, current_chart["Women Kurta Size Chart"]["Chest Circumference (cm)"])
            categorized_sizes["Gown"] = get_size(chest, current_chart["Gown Size Chart"]["Chest Circumference (cm)"])

    else:
        if "Chest Circumference (cm)" in normalized_measurements:
            chest = normalized_measurements["Chest Circumference (cm)"]
            categorized_sizes["Sherwani"] = get_size(chest, current_chart["Sherwani Size Chart"]["Chest Circumference (cm)"])
            categorized_sizes["Man Kurta"] = get_size(chest, current_chart["Man Kurta Size Chart"]["Chest Circumference (cm)"])
            categorized_sizes["Nehru Jackets"] = get_size(chest, current_chart["Nehru Jackets Size Chart"]["Chest Circumference (cm)"])

    return categorized_sizes

def main(front_view_image_path, side_view_image_path, user_height_cm, output_file_path="analysis_results.txt"):
    output_file = open(output_file_path, "w")

    def print_and_log(*args, **kwargs):
        print(*args, **kwargs)
        print(*args, file=output_file, **kwargs)

    def print_to_console(*args, **kwargs):
        print(*args, **kwargs)

    try:
        print_to_console("--- Starting Body Measurement Analysis ---")
        front_results, annotated_front_image = extract_keypoints(front_view_image_path)
        side_results, annotated_side_image = extract_keypoints(side_view_image_path)

        measurements = {}
        gender = "N/A"

        if front_results and front_results.pose_world_landmarks:
            print_and_log("\n--- Body Measurements Results ---")
            measurements = calculate_body_measurements(front_results.pose_world_landmarks.landmark, user_height_cm)
            if measurements:
                print_and_log(f"User Height: {measurements['user_height_cm']:.2f} cm")
                for key, value in measurements.items():
                    if key != "user_height_cm":
                        formatted_key = key.replace("_", " ").title()
                        print_and_log(f"{formatted_key}: {value:.2f} cm")
            print_and_log("---------------------------------")

        if annotated_front_image is not None:
            cv2.imwrite("annotated_front_view.jpg", annotated_front_image)
        if annotated_side_image is not None:
            cv2.imwrite("annotated_side_view.jpg", annotated_side_image)

        print_to_console("\n--- Starting Skin Tone & Gender Analysis ---")
       
        face_model_path = os.path.join(os.path.dirname(__file__), "model_weights", "face_detection_yunet_2023mar.onnx")
        pipeline = FashionAssistantPipeline(face_model_path, "pIufABh634G1BkWsQWSA")
        result = pipeline.analyze_image(front_view_image_path, generate_visualization=True)

        print_and_log("Results for Front View Image:")
        if "error" not in result:
            gender = result["gender"]
            print_and_log(f"  Skin Tone: {result['skin_tone']}")
            print_and_log(f"  Detected Gender: {gender} (Confidence: {result['gender_confidence']:.2f})")
            print_and_log(f"  Dominant Color (Hex): {result['hex_color']}")
            print_and_log(f"  Recommendations for {result['skin_tone']}:")
            print_and_log(f"    Best colors to wear: {', '.join(result['recommendations']['best'])}")
            print_and_log(f"    Avoid: {', '.join(result['recommendations']['avoid'])}")

        print_and_log("------------------------------------------")

        if measurements and gender != "N/A":
            print_and_log("\n--- Garment Size Categorization ---")
            categorized_sizes = categorize_garments(gender, measurements)
            for garment, size in categorized_sizes.items():
                print_and_log(f"  {garment}: {size}")
            print_and_log("-----------------------------------")
            print_and_log("\n--- Final Garment Size Recommendations ---")
            for garment, size in categorized_sizes.items():
                print_and_log(f"{garment}: {size}")
    finally:
        output_file.close()


if __name__ == "__main__":
    front_image = "./data/2/front_img.jpg"
    side_image = "./data/2/side_img.jpg"
    user_height = 159.0
    if os.path.exists(front_image) and os.path.exists(side_image):
        main(front_image, side_image, user_height)
    else:
        print("Error: Image paths are invalid.")

import os
import re
import random
from IPython.display import display, Image as IPImage


def parse_analysis_output(file_path):
    gender = None
    skin_tone = None
    best_colors = []
    avoid_colors = []
    measurements = {}
    sizes = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Gender
                if match := re.search(r"Detected Gender:\s*(\w+)", line, re.IGNORECASE):
                    gender = match.group(1).strip().capitalize()

                # Skin tone
                elif match := re.search(r"Skin Tone:\s*(.+)", line, re.IGNORECASE):
                    skin_tone = match.group(1).strip()

                # Best colors
                elif match := re.search(r"(?:Best|Recommended) colors(?: to wear)?:\s*(.+)", line, re.IGNORECASE):
                    best_colors = [c.strip().lower() for c in match.group(1).split(",") if c.strip()]

                # Avoid colors
                elif match := re.search(r"Avoid:\s*(.+)", line, re.IGNORECASE):
                    avoid_colors = [c.strip().lower() for c in match.group(1).split(",") if c.strip()]

                # Measurements
                elif ":" in line and "cm" in line.lower():
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip().replace("cm", "").strip()
                        try:
                            measurements[key] = float(val)
                        except ValueError:
                            continue

                # Sizes (style type : size)
                elif ":" in line:
                    parts = line.split(":")
                    if len(parts) == 2:
                        style = parts[0].strip()
                        val = parts[1].strip()
                        if val.upper() in ["S", "M", "L", "XL"]:
                            sizes[style] = val
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None, None, [], [], {}, {}

    return gender, skin_tone, best_colors, avoid_colors, measurements, sizes


import os
import random

import os
import random

def find_recommended_dress_images(dress_base_path, gender, recommended_colors, sizes):
    if not gender or not recommended_colors:
        return []

    recommended_colors_upper = [c.upper() for c in recommended_colors]

    if gender.lower() == 'male':
        style_folders = ['KURTA_MEN', 'NEHRU_JACKETS', 'SHERWANIS']
        gender_subfolder = 'Male'
    elif gender.lower() == 'female':
        style_folders = ['SAREES', 'LEHENGA', 'KURTI_WOMEN', 'GOWN']
        gender_subfolder = 'Female'
    else:
        return []

    base_gender_path = os.path.join(dress_base_path, gender_subfolder)
    if not os.path.isdir(base_gender_path):
        print(f"❌ Gender base path not found: {base_gender_path}")
        return []

    # 📁 Print available folders under Male/Female
    print("\n📁 Checking folders inside:", base_gender_path)
    try:
        print("Available folders:", os.listdir(base_gender_path))
    except Exception as e:
        print("❌ Error reading gender folder:", e)

    selected_images_with_metadata = []

    style_map = {
        "KURTA_MEN": "Man Kurta",
        "NEHRU_JACKETS": "Nehru Jackets",
        "SHERWANIS": "Sherwani",
        "LEHENGA": "Lehnga",
        "SAREES": "Saree Blouse",
        "KURTI_WOMEN": "Women Kurta",
        "GOWN": "Gown"
    }

    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))

    for style_folder in style_folders:
        style_path = os.path.join(base_gender_path, style_folder)
        if not os.path.isdir(style_path):
            print(f"❌ Skipping missing style folder: {style_path}")
            continue

        display_style_name = style_map.get(style_folder.upper(), style_folder.replace('_', ' ').title())
        associated_size = sizes.get(display_style_name) or "M"
        print(f"\n🔍 STYLE: {style_folder} → {display_style_name}, SIZE: {associated_size}")

        for color_folder in os.listdir(style_path):
            color_folder_path = os.path.join(style_path, color_folder)
            if not os.path.isdir(color_folder_path):
                continue

            if color_folder.strip().upper() in recommended_colors_upper:
                print(f"✅ MATCH in {display_style_name} → {color_folder}")
                image_files = [
                    f for f in os.listdir(color_folder_path)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')) and
                    os.path.isfile(os.path.join(color_folder_path, f))
                ]

                random.shuffle(image_files)
                for img_file in image_files[:2]:  # 2 per color
                    full_path = os.path.join(color_folder_path, img_file)
                    try:
                        rel_path = os.path.relpath(full_path, static_folder).replace("\\", "/")
                        web_path = f"/static/{rel_path}"
                        selected_images_with_metadata.append({
                            "image": web_path,
                            "type": display_style_name,
                            "size": associated_size
                        })
                    except Exception as e:
                        print(f"⚠️ Path error: {e}")

    random.shuffle(selected_images_with_metadata)
    return selected_images_with_metadata


def display_recommendations():
    analysis_file_path = os.path.join(os.path.dirname(__file__), "analysis_results.txt")
    dress_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "Dress"))

    if not os.path.isfile(analysis_file_path):
        print(f"❌ Analysis file not found: {analysis_file_path}")
        return
    if not os.path.isdir(dress_folder_path):
        print(f"❌ Dress folder not found: {dress_folder_path}")
        return

    gender, skin_tone, best_colors, avoid_colors, measurements, sizes = parse_analysis_output(analysis_file_path)

    print(f"Gender: {gender}")
    print(f"Skin Tone: {skin_tone}")
    print(f"Best Colors: {', '.join(best_colors)}")
    print(f"Avoid Colors: {', '.join(avoid_colors)}")
    print("Measurements:", measurements)
    print("Detected Sizes:", sizes)

    if not gender or not best_colors:
        print("⚠️ Insufficient data to display recommendations.")
        return

    # Pass the sizes dictionary to find_recommended_dress_images
    images_with_metadata = find_recommended_dress_images(dress_folder_path, gender, best_colors, sizes)

    if not images_with_metadata:
        print("⚠️ No dresses matched.")
        return

    for item in images_with_metadata:
        img_path = item["image"]
        style_name = item["type"]
        size = item["size"]

        html = f"""
        <div style='margin-bottom:30px;'>
            <h4>{style_name} (Size: {size})</h4>
            <img src="{img_path}" width="300px" style="border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">
        </div>
        """
        display(HTML(html))

    print("\n✅ Execution completed.")


if __name__ == "__main__":
    front_image = "./data/2/front_img.jpg"
    side_image = "./data/2/side_img.jpg"
    user_height = 159.0
    if os.path.exists(front_image) and os.path.exists(side_image):
        main(front_image, side_image, user_height)
    else:
        print("Error: Image paths are invalid.")


