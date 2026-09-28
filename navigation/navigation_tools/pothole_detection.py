import torch
# ---------------------------------------------------------
# Load pothole-trained YOLOv5 model ONCE
MODEL_PATH = "pothole_model.pt"
CONFIDENCE_THRESHOLD = 0.50
model = torch.hub.load(
    "ultralytics/yolov5",
    "custom",
    path=MODEL_PATH,
    force_reload=False
)
def detect_pothole(frame):
    # No frame = safest response
    if frame is None:
        return {
            "pothole_present": True,
            "command": "STOP"
        }
    frame_width = frame.shape[1]
    # Pothole detection
    results = model(frame)
    detections = results.xyxy[0]
    # Check every detected object
    for detection in detections:
        x1, y1, x2, y2, confidence, class_id = detection.tolist()
        if confidence < CONFIDENCE_THRESHOLD:
            continue
        class_id = int(class_id)
        class_name = model.names[class_id]
        # Only pothole detection
        if class_name.lower() != "pothole":
            continue
        # Find pothole center
        object_center_x = (x1 + x2) / 2
        # CENTER → STOP
        if frame_width * 0.30 <= object_center_x <= frame_width * 0.70:
            return {
                "pothole_present": True,
                "side": "CENTER",
                "command": "STOP",
                "confidence": round(confidence, 2)
            }
        # LEFT → slight right
        elif object_center_x < frame_width * 0.30:
            return {
                "pothole_present": True,
                "side": "LEFT",
                "command": "SR",
                "confidence": round(confidence, 2)
            }
        # RIGHT → slight left
        else:
            return {
                "pothole_present": True,
                "side": "RIGHT",
                "command": "SL",
                "confidence": round(confidence, 2)
            }
    # No pothole found
    return {
        "pothole_present": False,
        "side": None,
        "command": None
    }