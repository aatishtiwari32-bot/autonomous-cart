import cv2
camera_url = "0"
def get_frame(camera_url):
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print("Camera open nahi hua")
        return None
    success, frame = cap.read()
    cap.release()
    if not success:
        print("Frame nahi mila")
        return None
    return frame