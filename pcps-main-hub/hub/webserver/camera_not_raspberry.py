import cv2
import os
import threading
from datetime import datetime
from time import sleep
from glob import glob
import logging
from database.database_setup import db_handler
from disease_detection.restnetPDDD import disease_detection as analysis

# configure logging
cam_logger = logging.getLogger('CAMERA')
cam_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('camera.log')
fh.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

cam_logger.addHandler(fh)
cam_logger.addHandler(sh)


class ImageCaptureNotRaspberry:
    def __init__(self, camera_index=0, save_path='webserver/static/pictures/plant', max_images=5):
        self.camera_index = camera_index
        self.save_path = save_path
        self.capture_interval = 5  # seconds
        self.max_images = max_images
        self.lock = threading.Lock()
        self.ensure_directory_exists()
        self.index = 0 # analysis index
        self.analysis_interval = int(604800 / self.capture_interval) # analyse every 24h
        self.latest_path = None


    def ensure_directory_exists(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def capture_and_manage_images(self):
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            cam_logger.error("Error: Camera could not be opened.")
            return

        try:
            while True:
                success, frame = cap.read()
                if success:
                    self.save_and_manage_image(frame)
                else:
                    cam_logger.warning("Failed to capture image.")
        
                self.index += 1
                if self.index % self.analysis_interval == 0:
                    self.analyse_images()
                    
                sleep(self.capture_interval)
        except KeyboardInterrupt:
            cam_logger.info("Image capture interrupted.")
        finally:
            cap.release()  # Ensure the resource is released

    def save_and_manage_image(self, frame):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        image_path = os.path.join(self.save_path, f"captured_image_{timestamp}.jpg")
        cv2.imwrite(image_path, frame)
        cam_logger.info(f"Saved image: {image_path}")
        self.latest_path = image_path

        with self.lock:
            stored_images = glob(os.path.join(self.save_path, '*.jpg'))
            while len(stored_images) > self.max_images:
                oldest_image = min(stored_images, key=os.path.getmtime)
                os.remove(oldest_image)
                cam_logger.info(f"Deleted oldest image: {oldest_image}")
                stored_images.remove(oldest_image)
    
    def analyse_images(self):
        try:
            result = analysis(self.latest_path)
            with db_handler() as db:
                db.add_picture_analysis(self.latest_path, result[0], result[1], result[2])
            cam_logger.info(f"{self.latest_path} got analysed")
        except Exception as e:
            cam_logger.error(e)

if __name__ == '__main__':
    capture = ImageCaptureNotRaspberry()
    capture_thread = threading.Thread(target=capture.capture_and_manage_images)
    capture_thread.start()
