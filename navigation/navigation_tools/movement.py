from ultralytics import YOLO
model = YOLO("yolov8n.pt")
MIN_CONFIDENCE = 0.50
# Objects which can actually obstruct the cart
OBSTACLE_CLASSES = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "dog",
    "pothole",
    "kid"
}
def movement(frame):
    if frame is None:
        return {
            "obstacle_present": True,
            "side": "CENTER",
            "command": "STOP"
        }
    frame_width = frame.shape[1]
    path_left = frame_width * 0.30
    path_right = frame_width * 0.70

    side_left = frame_width * 0.15
    side_right = frame_width * 0.85
    # YOLO detection
    results = model(frame, verbose=False)
    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])
            if confidence < MIN_CONFIDENCE:
                continue
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            if class_name not in OBSTACLE_CLASSES:
                continue
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )
            object_center_x = (x1 + x2) / 2
            print(
                f"Object: {class_name} | "
                f"Confidence: {confidence:.2f} | "
                f"Center X: {object_center_x:.0f}"
            )
            if path_left <= object_center_x <= path_right:
                print(
                    f"{class_name} "
                    "detected in pathway → STOP"
                )
                return {
                    "obstacle_present": True,
                    "side": "CENTER",
                    "command": "STOP"
                }
            elif (
                side_left
                <= object_center_x
                < path_left
            ):
                print(
                    f"{class_name} "
                    "detected on LEFT → SLIGHT RIGHT"
                )
                return {
                    "obstacle_present": True,
                    "side": "LEFT",
                    "command": "SR"
                }
            elif (
                path_right
                < object_center_x
                <= side_right
            ):
                print(
                    f"{class_name} "
                    "detected on RIGHT → SLIGHT LEFT"
                )
                return {
                    "obstacle_present": True,
                    "side": "RIGHT",
                    "command": "SL"
                }
    return {
        "obstacle_present": False,
        "side": None,
        "command": None
    }