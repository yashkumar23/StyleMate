from flask import Blueprint, request, jsonify, session
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import hashlib
import re

from src.ai_models import main as ai_main

analysis_bp = Blueprint("analysis", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Your full standardized hex mapping
COLOR_HEX_MAP = {
    "BEIGE": "#F5F5DC",
    "BLACK": "#000000",
    "BLUE": "#0000FF",
    "BROWN": "#A52A2A",
    "CHARCOAL": "#36454F",
    "CREAM": "#FFFDD0",
    "GOLD": "#FFD700",
    "GRAY": "#808080",
    "GREEN": "#008000",
    "GREY": "#808080",
    "INDIGO": "#4B0082",
    "IVORY": "#FFFFF0",
    "KHAKI": "#F0E68C",
    "LAVENDER": "#E6E6FA",
    "MAGENTA": "#FF00FF",
    "MAROON": "#800000",
    "MULTICOLOR": "#D8BFD8",
    "MUSTARD": "#FFDB58",
    "NAVY": "#000080",
    "OFF_WHITE": "#FAF9F6",
    "OLIVE": "#808000",
    "ORANGE": "#FFA500",
    "PEACH": "#FFE5B4",
    "PINK": "#FFC0CB",
    "PURPLE": "#800080",
    "RED": "#FF0000",
    "SILVER": "#C0C0C0",
    "TEAL": "#008080",
    "TURQUOISE": "#40E0D0",
    "VIOLET": "#8F00FF",
    "WHITE": "#FFFFFF",
    "YELLOW": "#FFFF00"
}

def map_colors_to_hex(color_list):
    return [
        {"name": c, "hex": COLOR_HEX_MAP.get(c.upper(), "#CCCCCC")}
        for c in color_list
    ]

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_height(height):
    try:
        height_float = float(height)
        return 100 <= height_float <= 250
    except (ValueError, TypeError):
        return False

@analysis_bp.route("/api/analyze", methods=["POST"])
def analyze():
    front_image = request.files.get("front_view")
    side_image = request.files.get("side_view")
    height_cm = request.form.get("height")

    if not front_image or not side_image or not height_cm:
        return jsonify({"success": False, "message": "Missing inputs"}), 400
    if not validate_height(height_cm):
        return jsonify({"success": False, "message": "Invalid height"}), 400

    # Save uploaded images
    front_filename = f"front_{secure_filename(front_image.filename)}"
    side_filename = f"side_{secure_filename(side_image.filename)}"
    front_path = os.path.join(UPLOAD_FOLDER, front_filename)
    side_path = os.path.join(UPLOAD_FOLDER, side_filename)

    front_image.save(front_path)
    side_image.save(side_path)

    # Run AI model
    output_file = os.path.join("src", "ai_models", "analysis_results.txt")
    ai_main.main(front_path, side_path, float(height_cm), output_file_path=output_file)

    analysis = {}
    dresses = []
    sizes_from_analysis = {}

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or ":" not in line:
                continue

            # Measurement parsing
            measurement_match = re.match(r"(.+?):\s*([\d.]+)\s*cm", line)
            if measurement_match:
                key = measurement_match.group(1).strip().upper().replace(" ", "_")
                value = measurement_match.group(2).strip()
                analysis[key] = value
                continue

            # Gender
            if "Detected Gender" in line:
                analysis["GENDER"] = re.search(r"Detected Gender:\s*(\w+)", line).group(1).strip()
                continue

            # Skin tone
            if "Skin Tone" in line:
                analysis["SKIN_TONE"] = re.search(r"Skin Tone:\s*(.+)", line).group(1).strip()
                continue

            # Color recommendations
            if "Best colors to wear" in line or "Recommended colors" in line:
                colors = re.split(r",\s*", line.split(":")[1])
                analysis["COLOR_PALETTE"] = ",".join(colors)
                continue

            if "Avoid:" in line:
                avoid = re.split(r",\s*", line.split(":")[1])
                analysis["AVOID_COLORS"] = ",".join(avoid)
                continue
            
            # Sizes (style type : size) - Extract from analysis_results.txt
            style_size_match = re.match(r"\s*(Lehnga|Saree Blouse|Women Kurta|Gown|Sherwani|Man Kurta|Nehru Jackets):\s*(\w+)", line)
            if style_size_match:
                style = style_size_match.group(1)
                size = style_size_match.group(2)
                sizes_from_analysis[style] = size

        colors = [c.strip() for c in analysis.get("COLOR_PALETTE", "").split(",") if c.strip()]
        avoid = [c.strip() for c in analysis.get("AVOID_COLORS", "").split(",") if c.strip()]
        gender = analysis.get("GENDER", "")

        # Get dress image paths with metadata
        dress_base_path = os.path.abspath(os.path.join("src", "static", "Dress"))
        # Pass the extracted sizes to find_recommended_dress_images
        recommended_dresses_with_metadata = ai_main.find_recommended_dress_images(dress_base_path, gender, colors, sizes_from_analysis)

        # Populate dresses list with structured data
        for item in recommended_dresses_with_metadata:
            dresses.append({
                "dress_id": hashlib.md5((item["image"] + item["type"] + item["size"]).encode()).hexdigest(),
                "type": item["type"],
                "size": item["size"],
                "image": item["image"]
            })

    # ✅ Final result with mapped color hex
    result = {
        "analysis_result": {
            "gender": analysis.get("GENDER", ""),
            "skin_tone": analysis.get("SKIN_TONE", ""),
            "arm_length": analysis.get("ARM_LENGTH_CM", ""),
            "leg_length": analysis.get("LEG_LENGTH_CM", ""),
            "neck_to_waist": analysis.get("NECK_WAIST_LENGTH_FRONT_CM", ""),
            "shoulder_width": analysis.get("SHOULDER_WIDTH_CM", ""),
            "chest_circumference": analysis.get("CHEST_CIRCUMFERENCE_CM", ""),
            "color_palette": map_colors_to_hex(colors),
            "avoid_colors": map_colors_to_hex(avoid)
        },
        "recommended_dresses": dresses
    }

    # Save in session
    analysis_id = str(uuid.uuid4())
    sessions = session.get("analysis_sessions", {})
    sessions[analysis_id] = result
    session["analysis_sessions"] = sessions
    session["analysis_result"] = result
    session["analysis_id"] = analysis_id
    session.modified = True

    return jsonify({
        "success": True,
        "analysis_id": analysis_id,
        "data": result
    })

@analysis_bp.route("/api/analysis-result", methods=["GET"])
def get_analysis_result():
    analysis_id = request.args.get("analysis_id")
    if not analysis_id:
        return jsonify({"success": False, "message": "Missing analysis ID"}), 400

    sessions = session.get("analysis_sessions", {})
    if analysis_id in sessions:
        return jsonify({"success": True, "data": sessions[analysis_id]})
    else:
        return jsonify({"success": False, "message": "Analysis result not found or expired"}), 404

@analysis_bp.route("/debug-session")
def debug_session():
    return jsonify(dict(session))


