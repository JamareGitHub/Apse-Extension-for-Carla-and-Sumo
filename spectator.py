import carla
import numpy as np
import cv2
import time

class CarlaCameraClient:
    def __init__(self, host='127.0.0.1', port=2000):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.blueprint_library = self.world.get_blueprint_library()
        self.camera = None
        self.vehicles = []
        self.current_vehicle_index = -1
        self.image_data = None
        self.exit_flag = False
        # Initialize OpenCV window
        cv2.namedWindow('Camera Output', cv2.WINDOW_NORMAL)

    def get_all_vehicles(self):     
        """Retrieve all vehicles in the world."""
        while len(self.vehicles) == 0:
            print("Searching for vehicles...")
            self.world.wait_for_tick()
            self.vehicles = self.world.get_actors().filter("vehicle.*")
        print(f"Found {len(self.vehicles)} vehicles")

    def attach_camera_to_vehicle(self, vehicle):
        """Attach a camera to a given vehicle."""
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
        
        camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '640')
        camera_bp.set_attribute('image_size_y', '480')
        camera_bp.set_attribute('fov', '110')

        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        self.camera.listen(lambda image: self.process_image(image))
        print(f"Camera attached to vehicle {vehicle.type_id} at {vehicle.get_location()}")

    def process_image(self, image):
        """Process the image from the camera sensor."""
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]  # Remove alpha channel
        array = array[:, :, ::-1]  # Convert RGB to BGR
        self.image_data = array

    def display_camera_output(self):
        """Display the camera output using OpenCV."""
        if self.image_data is not None:
            cv2.imshow('Camera Output', self.image_data)
        else:
            print("No image data to display.")

    def switch_vehicle(self):
        """Switch the camera to the next vehicle."""
        if not self.vehicles:
            print("No vehicles available to switch.")
            return

        self.current_vehicle_index = (self.current_vehicle_index + 1) % len(self.vehicles)
        vehicle = self.vehicles[self.current_vehicle_index]
        print(f"Switching to vehicle {vehicle.type_id} at {vehicle.get_location()}")

        self.attach_camera_to_vehicle(vehicle)
        print("Vehicle switched and camera attached.")
        time.sleep(1)  # Explicit delay to ensure camera feed initialization

    def run(self):
        """Run the main loop to display camera output and switch vehicles."""
        self.get_all_vehicles()
        if not self.vehicles:
            print("No vehicles to attach camera to. Exiting.")
            return

        self.switch_vehicle()

        print("Press 'n' to switch to the next vehicle. Press 'q' to quit.")
        
        while not self.exit_flag:
            self.display_camera_output()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('n'):
                print("Switching vehicle...")
                self.switch_vehicle()
            elif key == ord('q'):
                print("Exiting...")
                self.exit_flag = True
            elif cv2.getWindowProperty('Camera Output', cv2.WND_PROP_VISIBLE) < 1:
                print("Window closed by user.")
                self.exit_flag = True

            # Add checks after switching vehicles
            if self.camera is None:
                print("Camera is None after switching vehicle.")
            if self.image_data is None:
                print("Image data is None after switching vehicle.")
        
        self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up resources...")
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        client = CarlaCameraClient()
        client.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        if client:
            client.cleanup()
