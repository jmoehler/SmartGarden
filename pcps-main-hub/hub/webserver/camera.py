import os
import threading
from datetime import datetime
from time import sleep
from glob import glob

from database.database_setup import db_handler
from disease_detection.restnetPDDD import disease_detection as analysis
import logging
import subprocess

# configure logging
cam_logger = logging.getLogger('CAMERA')
cam_logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
cam_logger.addHandler(sh)


class ImageCapture:
    def __init__(self, save_path='webserver/static/pictures/plant', max_images=5):
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
        try:
            while True:
                self.capture_image_with_libcamera()
                cam_logger.info("Image got analyzed")
                
                self.index += 1
                if self.index % self.analysis_interval == 0:
                    self.analyse_images()

                sleep(self.capture_interval)
        except KeyboardInterrupt:
            cam_logger.info("Image capture interrupted.")

    def capture_image_with_libcamera(self):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        image_path = os.path.join(self.save_path, f"captured_image_{timestamp}.jpg")
        try:
            # Adding the --nopreview option to disable preview
            subprocess.run(['libcamera-still', '--nopreview', '-o', image_path], check=True)
            cam_logger.info(f"Saved image: {image_path}")
            self.manage_images()
        except subprocess.CalledProcessError as e:
            cam_logger.error(f"Failed to capture image: {e}")
        self.latest_path = image_path

    def manage_images(self):
        with self.lock:
            stored_images = glob(os.path.join(self.save_path, '*.jpg'))
            while len(stored_images) > self.max_images:
                oldest_image = min(stored_images, key=os.path.getctime)
                os.remove(oldest_image)
                cam_logger.info(f"Deleted oldest image: {oldest_image}")
                stored_images.remove(oldest_image)
    
    def analyse_images(self):
        result = analysis(self.latest_path)
        with db_handler() as db:
            db.add_picture_analysis(self.latest_path, result[0], result[1], result[2])
        cam_logger.info(f"{self.latest_path} got analysed")


if __name__ == '__main__':
    capture = ImageCapture()
    capture_thread = threading.Thread(target=capture.capture_and_manage_images)
    capture_thread.start()
