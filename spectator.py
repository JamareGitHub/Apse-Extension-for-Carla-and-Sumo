import carla
import numpy as np
import cv2
import os
import time

class CarlaCameraClient:
    def __init__(self, host='127.0.0.1', port=2000, icon_folder='./icons'):
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
        self.current_location = None  # Track current location for speed calculation
        self.previous_location = None  # Track previous location for speed calculation
        self.current_location_timestamp = None  # Timestamp for current location
        self.previous_location_timestamp = None  # Timestamp for previous location

        self.first_person_location = [-.1, -.3, 1.3]  # Camera position

        # Initialize OpenCV window
        cv2.namedWindow('Camera Output', cv2.WINDOW_NORMAL)

        # Load icons from the specified folder
        self.icon_folder = icon_folder
        self.icons = self.load_icons()

    def load_icons(self):
        """Load all icons from the specified folder."""
        icons = {}
        for file in os.listdir(self.icon_folder):
            if file.endswith(".png"):  # Check if the file is a PNG image
                icon_path = os.path.join(self.icon_folder, file)  # Get the full path of the icon
                icon_name = os.path.splitext(file)[0]  # Get the icon name without extension
                icons[icon_name] = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)  # Load the icon with transparency
        return icons

    def get_all_vehicles(self):
        """Retrieve all vehicles in the world."""
        self.vehicles = []  # Reset vehicles so during switch vehicle new cars can be found and old vanish from list
        while len(self.vehicles) == 0:
            self.world.wait_for_tick()
            self.vehicles = self.world.get_actors().filter("vehicle.*")
        print(f"Found {len(self.vehicles)} vehicles")

    def clear_old_vehicle(self):
        """Clear the old vehicle and reset locations."""
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
        self.current_location = None
        self.previous_location = None
        self.current_location_timestamp = None
        self.previous_location_timestamp = None

    def set_first_person_cameralocation(self, vehicle):
        """Set the first-person camera location based on vehicle type."""
        vehicle_name = vehicle.type_id
        if vehicle_name == "vehicle.audi.a2":
            self.first_person_location = [0.2, -0.3, 1.3]
        elif vehicle_name == "vehicle.audi.tt":
            self.first_person_location = [0, -.3, 1.25]
        elif vehicle_name == "vehicle.jeep.wrangler_rubicon":
            self.first_person_location = [-0.3, -0.3, 1.5]
        elif vehicle_name == "vehicle.chevrolet.impala":
            self.first_person_location = [0.1, -0.3, 1.2]
        elif vehicle_name == "vehicle.mini.cooper_s":
            self.first_person_location = [-.1, -0.35, 1.2]
        elif vehicle_name == "vehicle.mercedes.coupe":
            self.first_person_location = [-.1, -0.3, 1.25]
        elif vehicle_name == "vehicle.bmw.grandtourer":
            self.first_person_location = [0, -.3, 1.35]
        elif vehicle_name == "vehicle.citroen.c3":
            self.first_person_location = [-.1, -0.3, 1.3]
        elif vehicle_name == "vehicle.ford.mustang":
            self.first_person_location = [-.2, -0.3, 1.1]
        elif vehicle_name == "vehicle.volkswagen.t2":
            self.first_person_location = [1, -0.35, 1.65]
        elif vehicle_name == "vehicle.lincoln.mkz_2017":
            self.first_person_location = [0, -0.3, 1.3]
        elif vehicle_name == "vehicle.seat.leon":
            self.first_person_location = [0.1, -0.3, 1.3]
        elif vehicle_name == "vehicle.nissan.patrol":
            self.first_person_location = [-.1, -0.3, 1.5]
        else:
            print("Vehicle type not found, using default camera position")
            self.first_person_location = [-.1, -0.3, 1.3]

    def attach_camera_to_vehicle(self, vehicle):
        """Attach a camera to a given vehicle."""
        self.clear_old_vehicle()
        camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '1920')
        camera_bp.set_attribute('image_size_y', '1080')
        camera_bp.set_attribute('fov', '90')

        self.set_first_person_cameralocation(vehicle)
        camera_transform = carla.Transform(carla.Location(x=self.first_person_location[0], y=self.first_person_location[1], z=self.first_person_location[2]))
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        self.camera.listen(lambda image: self.process_image(image))
        self.vehicle = vehicle  # Store the current vehicle
        print(f"Camera attached to vehicle {vehicle.type_id} at {vehicle.get_location()}")

    def process_image(self, image):
        """Process the image from the camera sensor."""
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        self.image_data = array.copy()  # Make the array writable by copying it

    def display_camera_output(self):
        """Display the camera output using OpenCV."""
        if self.image_data is not None:
            
            hud_image = self.image_data.copy()# Create a copy of the image to draw the HUD
            self.get_vehicle_speed()# Get the vehicle speed
            self.add_hud(hud_image)# Overlay the HUD on the copy of the image
            cv2.imshow('Camera Output', hud_image)# Display the combined image

    def get_vehicle_speed(self):
        """Get the speed of the current vehicle."""
        if self.vehicle is not None:
            self.current_location = self.vehicle.get_location()
            self.current_location_timestamp = time.time()
            if self.previous_location is None or self.previous_location_timestamp is None:
                self.previous_location = self.current_location
                self.previous_location_timestamp = self.current_location_timestamp
            elif self.current_location_timestamp - self.previous_location_timestamp < 0.5:
                return self.speed
            else:
                distance = np.sqrt((self.current_location.x - self.previous_location.x) ** 2 +
                                   (self.current_location.y - self.previous_location.y) ** 2 +
                                   (self.current_location.z - self.previous_location.z) ** 2)
                period = self.current_location_timestamp - self.previous_location_timestamp
                self.speed = 3.6 * (distance / period)  # Convert m/s to km/h

                self.previous_location = self.current_location
                self.previous_location_timestamp = self.current_location_timestamp

    def add_hud(self, image):
        """Add the speed HUD to the image."""
        h, w, _ = image.shape  # Get the height and width of the input image

        # Calculate positions for the text and icons
        text_x = w // 2  # Center the text horizontally
        text_y_start = h // 2 - 30  # Center the text vertically, starting above the center
        icon_y = text_y_start - 60  # Position the icons above the text

        vehicle_name = f"Vehicle type: {self.vehicle.type_id}"  # Vehicle type text
        id_text = f"Vehicle ID: {self.vehicle.id}"  # Vehicle ID text
        speed_text = f"Speed: {self.speed:.2f} km/h"  # Speed text
        font = cv2.FONT_HERSHEY_SIMPLEX  # Font for the text

        # Get text size for centering
        text_size_vehicle = cv2.getTextSize(vehicle_name, font, 1, 1)[0]
        text_size_id = cv2.getTextSize(id_text, font, 1, 1)[0]
        text_size_speed = cv2.getTextSize(speed_text, font, 1, 1)[0]

        # Draw text centered on the screen
        cv2.putText(image, vehicle_name, (text_x - text_size_vehicle[0] // 2, text_y_start), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, id_text, (text_x - text_size_id[0] // 2, text_y_start + 30), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, speed_text, (text_x - text_size_speed[0] // 2, text_y_start + 60), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

        # Add icons to the image, centered
        icon_x_start = text_x - len(self.icons) * 30  # Calculate starting x position to center the icons
        for i, (name, icon) in enumerate(self.icons.items()):  # Iterate over loaded icons
            if icon is not None:  # Check if the icon is loaded correctly
                icon_h, icon_w, _ = icon.shape  # Get the icon dimensions
                icon_x = icon_x_start + i * (icon_w + 10)  # Calculate the x position for the icon
                alpha_s = icon[:, :, 3] / 255.0  # Get the alpha channel of the icon (transparency)
                alpha_l = 1.0 - alpha_s  # Inverse alpha for the background

                # Blend the icon with the image
                for c in range(0, 3):  # Iterate over color channels
                    image[icon_y:icon_y + icon_h, icon_x:icon_x + icon_w, c] = (alpha_s * icon[:, :, c] +
                                                                                alpha_l * image[icon_y:icon_y + icon_h, icon_x:icon_x + icon_w, c])

    def switch_vehicle(self):
        """Switch to the next available vehicle."""
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
                print(f"Error switching to vehicle: {str(e)}")
                print(f"Skipping vehicle {vehicle.type_id} due to error.")
                self.current_vehicle_index = (self.current_vehicle_index + 1) % num_vehicles
                if self.current_vehicle_index == 0:
                    print("No valid vehicles found to switch to.")
                    self.exit_flag = True
                    return

    def run(self):
        """Run the main loop to display camera output and switch vehicles."""
        self.switch_vehicle()
        print("Press 'n' to switch to the next vehicle. Press 'q' to quit.")
        while not self.exit_flag:
            if self.vehicle and self.vehicle.get_location().x == 0.0 and self.vehicle.get_location().y == 0.0 and self.vehicle.get_location().z == 0.0:
                print("Vehicle finished its route / got deleted, trying to switch to next vehicle")
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