import carla
import numpy as np
import cv2

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
        # Initialize OpenCV window
        cv2.namedWindow('Camera Output', cv2.WINDOW_NORMAL)

    def get_all_vehicles(self):     
        while len(self.vehicles)<=0:
            print("loop")
            self.world.wait_for_tick()
            self.vehicles=self.world.get_actors().filter("vehicle.*")
        if not self.vehicles:
            print("No vehicles found in the world.")
        else:
            print(f"Found {len(self.vehicles)} vehicles")


    def attach_camera_to_vehicle(self, vehicle):
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
            self.camera = None
        
        camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '640')
        camera_bp.set_attribute('image_size_y', '480')
        camera_bp.set_attribute('fov', '110')

        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        self.camera.listen(lambda image: self.process_image(image))

    def process_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]  # Remove alpha channel
        array = array[:, :, ::-1]  # Convert RGB to BGR
        self.image_data = array


    def display_camera_output(self):
        try:
            if self.image_data is not None:
                cv2.imshow('Camera Output', self.image_data)
        except Exception as e:
            print(f"Error displaying image: {e}")


    def switch_vehicle(self):
        if not self.vehicles:
            print("No vehicles available to switch.")
            return

        self.current_vehicle_index = (self.current_vehicle_index + 1) % len(self.vehicles)
        vehicle = self.vehicles[self.current_vehicle_index]
        print(f"Switching to vehicle {vehicle.type_id} at {vehicle.get_location()}")

        # Stop and destroy the current camera instance
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
            self.camera = None

        # Attach the camera to the new vehicle
        self.attach_camera_to_vehicle(vehicle)
        
    def run(self):
        self.get_all_vehicles()
        if not self.vehicles:
            print("No vehicles to attach camera to. Exiting.")
            return

        self.switch_vehicle()
        self.exit_flag = False

        print("Press 'n' to switch to the next vehicle. Press 'q' to quit.")
        
        while not self.exit_flag:
            self.display_camera_output()
            key = cv2.waitKey(1) & 0xFF
            if key == ord('n'):
                print("pressed n")
                self.switch_vehicle()
                print("n button press")
            elif key == ord('q'):
                print("pressed q")
                self.exit_flag = True
                print("q button press")
            
            if cv2.getWindowProperty('Camera Output', cv2.WND_PROP_VISIBLE) < 1:
                break


        self.cleanup()

    def cleanup(self):
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    client = CarlaCameraClient()
    client.run()