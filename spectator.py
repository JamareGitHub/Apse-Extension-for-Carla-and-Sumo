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
        self.vehicle = None  # Keep track of the current vehicle
        self.vehicles = []
        self.current_vehicle_index = -1
        self.image_data = None
        self.exit_flag = False
        self.speed = 0.0  # Store the speed of the vehicle
        self.current_location=None
        self.previous_location=None
        self.current_location_timestamp=None
        self.previous_location_timestamp=None
        # Initialize OpenCV window
        cv2.namedWindow('Camera Output', cv2.WINDOW_NORMAL)

    def get_all_vehicles(self):
        """Retrieve all vehicles in the world."""
        self.vehicles = [] #reset vehicles so during switch vehicle new cars can be found and old vanish from list
        while len(self.vehicles) == 0:
            self.world.wait_for_tick()
            self.vehicles = self.world.get_actors().filter("vehicle.*")
        print(f"Found {len(self.vehicles)} vehicles")

    def clear_old_vehicle(self):
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
        
        self.current_location=None
        self.previous_location=None
        self.current_location_timestamp=None
        self.previous_location_timestamp=None


    def attach_camera_to_vehicle(self, vehicle):
        """Attach a camera to a given vehicle."""
        self.clear_old_vehicle()
        
        camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '1920')
        camera_bp.set_attribute('image_size_y', '1080')
        camera_bp.set_attribute('fov', '110')

        camera_transform = carla.Transform(carla.Location(x=0.2, y= -0.2, z=1.5))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        self.camera.listen(lambda image: self.process_image(image))
        self.vehicle = vehicle  # Store the current vehicle
        print(f"Camera attached to vehicle {vehicle.type_id} at {vehicle.get_location()}")

    def process_image(self, image):
        """Process the image from the camera sensor."""
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        #array = array[:, :, :3]  # Remove alpha channel
        #array = array[:, :, ::-1]  # Convert RGB to BGR
        self.image_data = array.copy()  # Make the array writable by copying it

    def display_camera_output(self):
        """Display the camera output using OpenCV."""
        if self.image_data is not None:
            # Get the vehicle speed

            self.get_vehicle_speed()
            # Overlay the speed on the image
            self.add_hud(self.image_data)
            cv2.imshow('Camera Output', self.image_data)

    def get_vehicle_speed(self):
        """Get the speed of the current vehicle."""
        if self.vehicle is not None:
            self.current_location = self.vehicle.get_location()
            self.current_location_timestamp = time.time()
            if self.previous_location == None or self.previous_location_timestamp == None:
                self.previous_location=self.current_location
                self.previous_location_timestamp = self.current_location_timestamp
            elif self.current_location_timestamp - self.previous_location_timestamp < 0.5:
                return self.speed

            else:
                distance = np.sqrt((self.current_location.x - self.previous_location.x)**2 + (self.current_location.y - self.previous_location.y)**2 + (self.current_location.z - self.previous_location.z)**2)
                period = (self.current_location_timestamp - self.previous_location_timestamp)
                self.speed = 3.6 * (distance / period)#*3.6 für km/h statt m/s
                
                self.previous_location=self.current_location
                self.previous_location_timestamp = self.current_location_timestamp

    def add_hud(self, image):
        """Add the speed HUD to the image."""
        vehicle_name=f"Vehicle type: {self.vehicle.type_id }"
        id_text=f"Vehicle ID: {self.vehicle.id }"
        speed_text = f"Speed: {self.speed:.2f} km/h"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, vehicle_name, (10, 30), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, id_text, (10, 60), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, speed_text, (10, 90), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

    def switch_vehicle(self):
        self.get_all_vehicles()
        
        if not self.vehicles:
            print("No vehicles available to switch.")
            return

        num_vehicles = len(self.vehicles)
        self.current_vehicle_index = (self.current_vehicle_index + 1) % num_vehicles
        
        while True:
            vehicle = self.vehicles[self.current_vehicle_index]
            
            try:
                print(f"Switching to vehicle {vehicle.type_id} at {vehicle.get_location()}")
                
                self.attach_camera_to_vehicle(vehicle)
                print("Vehicle switched and sensors attached.")
                break  # Exit the loop if switching was successful
            except Exception as e:
                # Handle the case where the vehicle doesn't exist anymore
                print(f"Error switching to vehicle: {str(e)}")
                print(f"Skipping vehicle {vehicle.type_id} due to error.")
                
                # Move to the next vehicle
                self.current_vehicle_index = (self.current_vehicle_index + 1) % num_vehicles
                
                # If we have looped through all vehicles, exit the method
                if self.current_vehicle_index == 0:
                    print("No valid vehicles found to switch to.")
                    self.exit_flag = True
                    return
    
    def run(self):
        """Run the main loop to display camera output and switch vehicles."""
        self.switch_vehicle()

        print("Press 'n' to switch to the next vehicle. Press 'q' to quit.")
        
        while not self.exit_flag:
            #print(self.vehicle.is_alive)
            location=self.vehicle.get_location()
            if(location.x == 0.0 and location.y == 0.0 and location.z == 0.0):
                print("vehicle finished its route / got deleted, trying to switch to next vehicle")
                self.switch_vehicle()


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
