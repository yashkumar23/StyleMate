
import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints(image_path):
    """
    Extracts pose keypoints from an image using MediaPipe.

    Args:
        image_path (str): Path to the input image.

    Returns:
        tuple: A tuple containing:
            - results (mediapipe.python.solutions.pose.PoseLandmarkerResult): Pose estimation results.
            - image (numpy.ndarray): The input image with landmarks drawn.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return None, None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        results = pose.process(image_rgb)

        if not results.pose_landmarks:
            print("No pose landmarks detected.")
            return results, image

        # Draw the pose annotation on the image.
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

    return results, annotated_image

def calculate_euclidean_distance(point1, point2):
    """
    Calculates the Euclidean distance between two 3D points.

    Args:
        point1 (list or tuple): Coordinates of the first point (x, y, z).
        point2 (list or tuple): Coordinates of the second point (x, y, z).

    Returns:
        float: The Euclidean distance between the two points.
    """
    return np.linalg.norm(np.array(point1) - np.array(point2))

def get_landmark_coordinates(landmarks, landmark_index, scale_to_cm=False):
    """
    Retrieves the x, y, z coordinates of a specific landmark.

    Args:
        landmarks: MediaPipe landmarks object.
        landmark_index (int): Index of the landmark.
        scale_to_cm (bool): If True, scales the coordinates from meters to centimeters.

    Returns:
        tuple: (x, y, z) coordinates of the landmark.
    """
    if landmarks and landmark_index < len(landmarks):
        landmark = landmarks[landmark_index]
        if scale_to_cm:
            return (landmark.x * 100, landmark.y * 100, landmark.z * 100)
        else:
            return (landmark.x, landmark.y, landmark.z)
    return None

def calculate_body_measurements(world_landmarks, user_height_cm):
    """
    Calculates various body measurements in cm using MediaPipe world landmarks and user\'s height for scaling.

    Args:
        world_landmarks: MediaPipe world landmarks object (3D coordinates).
        user_height_cm (float): User\'s actual height in centimeters.

    Returns:
        dict: A dictionary containing calculated body measurements.
    """
    measurements = {}
    measurements["user_height_cm"] = user_height_cm

    # Define keypoint indices for easier access
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32

    # Get 3D world coordinates of relevant landmarks in cm
    # We pass scale_to_cm=True to get coordinates directly in centimeters
    l_shoulder = get_landmark_coordinates(world_landmarks, LEFT_SHOULDER, scale_to_cm=True)
    r_shoulder = get_landmark_coordinates(world_landmarks, RIGHT_SHOULDER, scale_to_cm=True)
    l_elbow = get_landmark_coordinates(world_landmarks, LEFT_ELBOW, scale_to_cm=True)
    r_elbow = get_landmark_coordinates(world_landmarks, RIGHT_ELBOW, scale_to_cm=True)
    l_wrist = get_landmark_coordinates(world_landmarks, LEFT_WRIST, scale_to_cm=True)
    r_wrist = get_landmark_coordinates(world_landmarks, RIGHT_WRIST, scale_to_cm=True)
    l_hip = get_landmark_coordinates(world_landmarks, LEFT_HIP, scale_to_cm=True)
    r_hip = get_landmark_coordinates(world_landmarks, RIGHT_HIP, scale_to_cm=True)
    l_knee = get_landmark_coordinates(world_landmarks, LEFT_KNEE, scale_to_cm=True)
    r_knee = get_landmark_coordinates(world_landmarks, RIGHT_KNEE, scale_to_cm=True)
    l_ankle = get_landmark_coordinates(world_landmarks, LEFT_ANKLE, scale_to_cm=True)
    r_ankle = get_landmark_coordinates(world_landmarks, RIGHT_ANKLE, scale_to_cm=True)
    nose = get_landmark_coordinates(world_landmarks, NOSE, scale_to_cm=True)
    l_heel = get_landmark_coordinates(world_landmarks, LEFT_HEEL, scale_to_cm=True)
    r_heel = get_landmark_coordinates(world_landmarks, RIGHT_HEEL, scale_to_cm=True)
    l_foot_index = get_landmark_coordinates(world_landmarks, LEFT_FOOT_INDEX, scale_to_cm=True)
    r_foot_index = get_landmark_coordinates(world_landmarks, RIGHT_FOOT_INDEX, scale_to_cm=True)
    left_ear = get_landmark_coordinates(world_landmarks, LEFT_EAR, scale_to_cm=True)
    right_ear = get_landmark_coordinates(world_landmarks, RIGHT_EAR, scale_to_cm=True)

    # Calculate reference height for scaling (nose to midpoint of heels/foot_index)
    reference_height_mp = 0.0
    if nose and l_heel and r_heel:
        mid_heel = ((l_heel[0] + r_heel[0]) / 2, (l_heel[1] + r_heel[1]) / 2, (l_heel[2] + r_heel[2]) / 2)
        reference_height_mp = calculate_euclidean_distance(nose, mid_heel)
    elif nose and l_foot_index and r_foot_index:
        mid_foot_index = ((l_foot_index[0] + r_foot_index[0]) / 2, (l_foot_index[1] + r_foot_index[1]) / 2, (l_foot_index[2] + r_foot_index[2]) / 2)
        reference_height_mp = calculate_euclidean_distance(nose, mid_foot_index)
    elif left_ear and right_ear and l_heel and r_heel:
        mid_ear = ((left_ear[0] + right_ear[0]) / 2, (left_ear[1] + right_ear[1]) / 2, (left_ear[2] + right_ear[2]) / 2)
        mid_heel = ((l_heel[0] + r_heel[0]) / 2, (l_heel[1] + r_heel[1]) / 2, (l_heel[2] + r_heel[2]) / 2)
        reference_height_mp = calculate_euclidean_distance(mid_ear, mid_heel)
    elif left_ear and right_ear and l_foot_index and r_foot_index:
        mid_ear = ((left_ear[0] + right_ear[0]) / 2, (left_ear[1] + right_ear[1]) / 2, (left_ear[2] + right_ear[2]) / 2)
        mid_foot_index = ((l_foot_index[0] + r_foot_index[0]) / 2, (l_foot_index[1] + r_foot_index[1]) / 2, (l_foot_index[2] + r_foot_index[2]) / 2)
        reference_height_mp = calculate_euclidean_distance(mid_ear, mid_foot_index)

    if reference_height_mp == 0:
        print("Could not calculate reference height for scaling. Missing essential landmarks.")
        return measurements

    scaling_factor = user_height_cm / reference_height_mp

    # Shoulder Length (using shoulder width as proxy)
    if l_shoulder and r_shoulder:
        original_calculated_shoulder_width = calculate_euclidean_distance(l_shoulder, r_shoulder) * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_SHOULDER = 1.1899556759836496
        CALIBRATION_INTERCEPT_SHOULDER = -1.0431462778778453
        calibrated_shoulder_width = (CALIBRATION_SLOPE_SHOULDER * original_calculated_shoulder_width) + CALIBRATION_INTERCEPT_SHOULDER
        measurements["shoulder_width_cm"] = max(0, calibrated_shoulder_width)

    # Overall Arm Length (average of left and right)
    arm_length_left = 0.0
    if l_shoulder and l_elbow and l_wrist:
        arm_length_left = calculate_euclidean_distance(l_shoulder, l_elbow) + calculate_euclidean_distance(l_elbow, l_wrist)

    arm_length_right = 0.0
    if r_shoulder and r_elbow and r_wrist:
        arm_length_right = calculate_euclidean_distance(r_shoulder, r_elbow) + calculate_euclidean_distance(r_elbow, r_wrist)

    if arm_length_left > 0 and arm_length_right > 0:
        original_calculated_arm_length = ((arm_length_left + arm_length_right) / 2) * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_ARM = 0.1409478597075848
        CALIBRATION_INTERCEPT_ARM = 50.85913441804667
        calibrated_arm_length = (CALIBRATION_SLOPE_ARM * original_calculated_arm_length) + CALIBRATION_INTERCEPT_ARM
        measurements["arm_length_cm"] = max(0, calibrated_arm_length)
    elif arm_length_left > 0:
        original_calculated_arm_length = arm_length_left * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_ARM = 0.1409478597075848
        CALIBRATION_INTERCEPT_ARM = 50.85913441804667
        calibrated_arm_length = (CALIBRATION_SLOPE_ARM * original_calculated_arm_length) + CALIBRATION_INTERCEPT_ARM
        measurements["arm_length_cm"] = max(0, calibrated_arm_length)
    elif arm_length_right > 0:
        original_calculated_arm_length = arm_length_right * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_ARM = 0.1409478597075848
        CALIBRATION_INTERCEPT_ARM = 50.85913441804667
        calibrated_arm_length = (CALIBRATION_SLOPE_ARM * original_calculated_arm_length) + CALIBRATION_INTERCEPT_ARM
        measurements["arm_length_cm"] = max(0, calibrated_arm_length)

    # Overall Leg Length (average of left and right - Hip to Ankle)
    leg_length_left = 0.0
    if l_hip and l_knee and l_ankle:
        leg_length_left = calculate_euclidean_distance(l_hip, l_knee) + calculate_euclidean_distance(l_knee, l_ankle)

    leg_length_right = 0.0
    if r_hip and r_knee and r_ankle:
        leg_length_right = calculate_euclidean_distance(r_hip, r_knee) + calculate_euclidean_distance(r_knee, r_ankle)

    if leg_length_left > 0 and leg_length_right > 0:
        original_calculated_leg_length = ((leg_length_left + leg_length_right) / 2) * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_LEG = 0.4453700901684382
        CALIBRATION_INTERCEPT_LEG = 54.86505394870431
        calibrated_leg_length = (CALIBRATION_SLOPE_LEG * original_calculated_leg_length) + CALIBRATION_INTERCEPT_LEG
        measurements["leg_length_cm"] = max(0, calibrated_leg_length)
    elif leg_length_left > 0:
        original_calculated_leg_length = leg_length_left * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_LEG = 0.4453700901684382
        CALIBRATION_INTERCEPT_LEG = 54.86505394870431
        calibrated_leg_length = (CALIBRATION_SLOPE_LEG * original_calculated_leg_length) + CALIBRATION_INTERCEPT_LEG
        measurements["leg_length_cm"] = max(0, calibrated_leg_length)
    elif leg_length_right > 0:
        original_calculated_leg_length = leg_length_right * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_LEG = 0.4453700901684382
        CALIBRATION_INTERCEPT_LEG = 54.86505394870431
        calibrated_leg_length = (CALIBRATION_SLOPE_LEG * original_calculated_leg_length) + CALIBRATION_INTERCEPT_LEG
        measurements["leg_length_cm"] = max(0, calibrated_leg_length)

    # Waist Circumference (Approximation)
    if l_hip and r_hip and l_shoulder and r_shoulder:
        hip_width = calculate_euclidean_distance(l_hip, r_hip)
        shoulder_width = calculate_euclidean_distance(l_shoulder, r_shoulder)
        waist_depth_proxy = hip_width * 0.7
        original_calculated_waist_circumference = np.pi * (hip_width + waist_depth_proxy) / 2 * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_WAIST = 1.3773507316229983
        CALIBRATION_INTERCEPT_WAIST = -7.846180925536487
        calibrated_waist_circumference = (CALIBRATION_SLOPE_WAIST * original_calculated_waist_circumference) + CALIBRATION_INTERCEPT_WAIST
        measurements["waist_circumference_cm"] = max(0, calibrated_waist_circumference)

    # Hip Circumference (Approximation)
    if l_hip and r_hip:
        hip_width = calculate_euclidean_distance(l_hip, r_hip)
        hip_depth_proxy = hip_width * 0.9
        original_calculated_hip_circumference = np.pi * (hip_width + hip_depth_proxy) / 2 * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_HIP = -0.17787247854129987 # Using hips_circumference_cm coefficients for hip_circumference_cm
        CALIBRATION_INTERCEPT_HIP = 100.69807736071145 # Using hips_circumference_cm coefficients for hip_circumference_cm
        calibrated_hip_circumference = (CALIBRATION_SLOPE_HIP * original_calculated_hip_circumference) + CALIBRATION_INTERCEPT_HIP
        measurements["hip_circumference_cm"] = max(0, calibrated_hip_circumference)

    # Chest Circumference (Approximation) - This is already calibrated, so no changes here.
    if l_shoulder and r_shoulder:
        chest_width = calculate_euclidean_distance(l_shoulder, r_shoulder)
        chest_depth_proxy = chest_width * 0.8
        original_calculated_chest_circumference = np.pi * (chest_width + chest_depth_proxy) / 2 * scaling_factor
        CALIBRATION_SLOPE_CHEST = 0.9049
        CALIBRATION_INTERCEPT_CHEST = 5.7647
        calibrated_chest_circumference = (CALIBRATION_SLOPE_CHEST * original_calculated_chest_circumference) + CALIBRATION_INTERCEPT_CHEST
        measurements["chest_circumference_cm"] = max(0, calibrated_chest_circumference)

    # Thigh Circumference (Approximation)
    if l_hip and l_knee and r_hip and r_knee:
        thigh_length_left = calculate_euclidean_distance(l_hip, l_knee)
        thigh_length_right = calculate_euclidean_distance(r_hip, r_knee)
        avg_thigh_length = (thigh_length_left + thigh_length_right) / 2
        thigh_circumference_proxy = avg_thigh_length * 0.6
        original_calculated_thigh_circumference = thigh_circumference_proxy * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_THIGH = -0.155056156106795
        CALIBRATION_INTERCEPT_THIGH = 60.401846072473674
        calibrated_thigh_circumference = (CALIBRATION_SLOPE_THIGH * original_calculated_thigh_circumference) + CALIBRATION_INTERCEPT_THIGH
        measurements["thigh_circumference_cm"] = max(0, calibrated_thigh_circumference)

    # Neck to Waist Length
    if l_shoulder and r_shoulder and l_hip and r_hip:
        neck_base = ((l_shoulder[0] + r_shoulder[0]) / 2, (l_shoulder[1] + r_shoulder[1]) / 2, (l_shoulder[2] + r_shoulder[2]) / 2)
        waist_mid = ((l_hip[0] + r_hip[0]) / 2, (l_hip[1] + r_hip[1]) / 2, (l_hip[2] + r_hip[2]) / 2)
        original_calculated_neck_waist_length = calculate_euclidean_distance(neck_base, waist_mid) * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_NECK_WAIST = 0.4567544013191312
        CALIBRATION_INTERCEPT_NECK_WAIST = 23.46707367877659
        calibrated_neck_waist_length = (CALIBRATION_SLOPE_NECK_WAIST * original_calculated_neck_waist_length) + CALIBRATION_INTERCEPT_NECK_WAIST
        measurements["neck_waist_length_front_cm"] = max(0, calibrated_neck_waist_length)

    # Neck Circumference (Approximation)
    if l_shoulder and r_shoulder:
        shoulder_width_for_neck = calculate_euclidean_distance(l_shoulder, r_shoulder)
        neck_width_proxy = shoulder_width_for_neck * 0.3
        neck_depth_proxy = neck_width_proxy * 0.8
        original_calculated_neck_circumference = np.pi * (neck_width_proxy + neck_depth_proxy) / 2 * scaling_factor
        # Apply linear regression calibration
        CALIBRATION_SLOPE_NECK = 1.158162581279468
        CALIBRATION_INTERCEPT_NECK = 2.1186255936021183
        calibrated_neck_circumference = (CALIBRATION_SLOPE_NECK * original_calculated_neck_circumference) + CALIBRATION_INTERCEPT_NECK
        measurements["neck_circumference_cm"] = max(0, calibrated_neck_circumference)

    return measurements


