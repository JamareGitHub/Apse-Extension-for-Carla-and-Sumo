import carla
import numpy as np
import cv2
import os
import time
import xml.etree.ElementTree as ET

from collections import deque

class CarlaCameraClient:
    def __init__(self, host='127.0.0.1', port=2000):
        # Initialize the CARLA client and world
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
        self.hudname = 'HUD'

        # Speed-related attributes
        self.speed = 0.0  # Store the speed of the vehicle
        self.current_location = None  # Track current location for speed calculation
        self.previous_location = None  # Track previous location for speed calculation
        self.current_location_timestamp = None  # Timestamp for current location
        self.previous_location_timestamp = None  # Timestamp for previous location
        self.speed_history = deque(maxlen=100)  # Store the last 100 speed measurements for smoothing
        self.smoothing_timestamp = None
        self.speed_hud_location = (0.60, 0.45)

        # Camera configuration
        self.first_person_location = [-.1, -.3, 1.3]  # Camera position
        self.image_resolution_x = '1920'
        self.image_resolution_y = '1080'

        # HUD icons configuration
        self.icon_path = "icons/"
        self.icons = {
            'icon_stopwatch': ('stopwatch-svgrepo-com.png'),

            'icon_battery': ('battery-svgrepo-com.png'),#höhe , breite
            'icon_calendar': ('calendar-svgrepo-com.png'),
            'icon_clock': ('clock-svgrepo-com.png'),
            'icon_music_player': ('music-player-svgrepo-com.png'),
            'icon_smartphone': ('smartphone-svgrepo-com.png'),
            'icon_speaker': ('speaker-svgrepo-com.png'),
            'icon_compass': ('compass-svgrepo-com.png'),
            'icon_placeholder': ('placeholder-svgrepo-com.png'),


            'icon_idea': ('idea-svgrepo-com.png'),
            'icon_minus': ('minus-svgrepo-com.png'),
            'icon_navigation': ('navigation-svgrepo-com.png')

            # Add more icons as needed
        }  
        self.icon_positions = [
            (0.40, 0.45),#1
            (0.60, 0.35),#2
            (0.60, 0.55),#3
            (0.60, 0.25),#4
            (0.60, 0.65),#5
            (0.40, 0.35),#6
            (0.40, 0.55),#7
            (0.40, 0.25),#8
            (0.40, 0.65),#9
            (0.60, 0.15),#10
            (0.60, 0.75)#11
            
        ]
        self.show_speed_text = False
        self.show_icon_stopwatch = False
        self.show_icon_battery = False
        self.show_icon_calendar = False
        self.show_icon_clock = False
        self.show_icon_idea = False
        self.show_icon_music_player = False
        self.show_icon_navigation = False
        self.show_icon_smartphone = False
        self.show_icon_speaker = False
        self.show_icon_compass = False
        self.show_icon_minus = False
        self.show_icon_placeholder = False
        self.hud_alpha = 1
        self.iconscale = (90,90)

        # Initialize OpenCV window
        cv2.namedWindow('Camera Output', cv2.WINDOW_NORMAL)
        
        # Initialize with the XML configuration file
        self.hud_xml_config = self.load_xml_config("hudconfig.xml")

    def load_xml_config(self, xml_file):
        """Load the XML configuration file."""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        config = {}
        for vehicle in root.findall('Vehicle'):
            type_id = vehicle.get('type_id')
            if type_id:
                HUDName = vehicle.find('HUDName').text
                brightness = vehicle.find('Brightness').text
                density = vehicle.find('Density').text
                relevance = vehicle.find('Relevance').text
                fov = vehicle.find('FoV').text
                config[type_id] = {
                    'HUDName': HUDName,
                    'Brightness': brightness,
                    'Density': density,
                    'Relevance': relevance,
                    'FoV': fov
                }
        return config
    
    def set_xml_config(self, vehicle):
        """Set HUD configuration based on XML for a specific vehicle type."""
        if vehicle.type_id in self.hud_xml_config:
            config = self.hud_xml_config[vehicle.type_id]
            self.hudname = config.get('HUDName')
            brightness = config.get('Brightness')
            density = config.get('Density')
            relevance = config.get('Relevance')
            fov = config.get('FoV')

            print(brightness)
            print(density)
            print(relevance)
            print(fov)
            
            if brightness == "very dark":
                self.hud_alpha = 1
            elif brightness == "dark":
                self.hud_alpha = 0.7
            elif brightness == "average":
                self.hud_alpha = 0.5
            elif brightness == "bright":
                self.hud_alpha = 0.3
            elif brightness == "very bright":
                self.hud_alpha = 0.1


            print(fov)
            if fov == "small":
                        self.iconscale = (90,90)
                        self.icon_positions = [
                            (0.60, 0.40),#2
                            (0.60, 0.50),#3
                            (0.60, 0.35),#4
                            (0.60, 0.55),#5
                            (0.60, 0.30),#10
                            (0.60, 0.60),#11
                            (0.50, 0.45),#1
                            (0.50, 0.50),#7
                            (0.50, 0.40),#6
                            (0.50, 0.55),#9
                            (0.50, 0.35)#8
                            
                        ]
            elif fov == "medium":
                        self.iconscale = (90,90)
                        self.icon_positions = [
                            (0.50, 0.45),#1
                            (0.60, 0.40),#2
                            (0.60, 0.50),#3
                            (0.60, 0.35),#4
                            (0.60, 0.55),#5
                            (0.50, 0.40),#6
                            (0.50, 0.50),#7
                            (0.50, 0.35),#8
                            (0.50, 0.55),#9
                            (0.60, 0.30),#10
                            (0.60, 0.60)#11
                        ]
            elif fov == "large":
                        self.iconscale = (90,90)
                        self.icon_positions = [
                            (0.40, 0.45),#1
                            (0.60, 0.35),#2
                            (0.60, 0.55),#3
                            (0.60, 0.25),#4
                            (0.60, 0.65),#5
                            (0.40, 0.35),#6
                            (0.40, 0.55),#7
                            (0.40, 0.25),#8
                            (0.40, 0.65),#9
                            (0.60, 0.15),#10
                            (0.60, 0.75)#11
                        ]


            if relevance == "unimportant":
                self.show_speed_text = True
                self.show_icon_stopwatch = True
                self.show_speed_text = True
                self.show_icon_battery = True
                self.show_icon_calendar = True
                self.show_icon_clock = True
                self.show_icon_idea = True
                self.show_icon_music_player = True
                self.show_icon_navigation = True
                self.show_icon_smartphone = True
                self.show_icon_speaker = True
                self.show_icon_compass = True
                self.show_icon_minus = True
                self.show_icon_placeholder = True
            elif relevance == "neutral":
                self.show_icon_stopwatch = True
                self.show_speed_text = True
                self.show_icon_clock = True
                self.show_icon_idea = True
                self.show_icon_navigation = True
                self.show_icon_minus = True
                self.show_icon_battery = True
            elif relevance == "important":
                self.speed_hud_location = (40,45)
                self.show_speed_text = True
                self.show_icon_navigation = True
                self.show_icon_minus = True 
        else:
            self.reset_hud()

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
        self.speed_history.clear()
        self.smoothing_timestamp = None
        self.reset_hud()

    def reset_hud(self):
        self.hudname = 'HUD'
        self.show_speed_text = False
        self.show_icon_stopwatch = False
        self.show_icon_battery = False
        self.show_icon_calendar = False
        self.show_icon_clock = False
        self.show_icon_idea = False
        self.show_icon_music_player = False
        self.show_icon_navigation = False
        self.show_icon_smartphone = False
        self.show_icon_speaker = False
        self.show_icon_compass = False
        self.show_icon_minus = False
        self.show_icon_placeholder = False
        self.hud_alpha = 1
        self.iconscale = (90,90)        
        self.icon_positions = [
            (0.60, 0.45),#0
            (0.50, 0.45),#1
            (0.60, 0.40),#2
            (0.60, 0.50),#3
            (0.60, 0.35),#4
            (0.60, 0.55),#5
            (0.50, 0.40),#6
            (0.50, 0.50),#7
            (0.50, 0.35),#8
            (0.50, 0.55),#9
            (0.60, 0.30),#10
            (0.60, 0.60)#11
            
        ]

    def set_vehicle_configuration(self, vehicle):
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
        camera_bp.set_attribute('image_size_x', self.image_resolution_x)
        camera_bp.set_attribute('image_size_y', self.image_resolution_y)
        camera_bp.set_attribute('fov', '90')

        self.set_vehicle_configuration(vehicle)
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
            self.add_hud(hud_image)# Overlay the HUD on the copy of the image
            cv2.imshow('Camera Output', hud_image)# Display the combined image

    def get_vehicle_speed(self):
        """Get the speed of the current vehicle."""
        if self.vehicle is not None:
            self.current_location = self.vehicle.get_location()
            self.current_location_timestamp = time.perf_counter()  # High-resolution timestamp

            if self.previous_location is None or self.previous_location_timestamp is None:
                self.previous_location = self.current_location
                self.previous_location_timestamp = self.current_location_timestamp
            else:
                distance = np.sqrt((self.current_location.x - self.previous_location.x) ** 2 +
                                (self.current_location.y - self.previous_location.y) ** 2 +
                                (self.current_location.z - self.previous_location.z) ** 2)
                period = self.current_location_timestamp - self.previous_location_timestamp

                # Calculate current speed in km/h and add to history
                current_speed = 3.6 * (distance / period)
                self.speed_history.append(round(current_speed))

                # Compute smoothed speed as the average of the speed history
                if (not self.smoothing_timestamp or (np.sqrt((self.current_location_timestamp-self.smoothing_timestamp)**2)>0.1)):
                    self.smoothing_timestamp=self.current_location_timestamp
                    self.speed = sum(self.speed_history) / len(self.speed_history)

                self.previous_location = self.current_location
                self.previous_location_timestamp = self.current_location_timestamp

    def add_hud(self, image):
        """Add the speed HUD to the image."""
        h, w, _ = image.shape  # Get the height and width of the input image

        # Calculate positions for the text and icons
        text_x = w // 2  # Center the text horizontally
        text_y_start = h // 2 - 30  # Center the text vertically, starting above the center
        
        vehicle_name = f"Vehicle type: {self.vehicle.type_id}"  # Vehicle type text
        id_text = f"Vehicle ID: {self.vehicle.id}"  # Vehicle ID text
        hudname_text = f"HUD Name: {self.hudname}" #HUD Name text
        font = cv2.FONT_HERSHEY_SIMPLEX  # Font for the text

        # Get text size for centering
        text_size_vehicle = cv2.getTextSize(vehicle_name, font, 1, 1)[0]
        text_size_id = cv2.getTextSize(id_text, font, 1, 1)[0]

        # Draw text centered on the screen
        cv2.putText(image, hudname_text, (text_x - text_size_vehicle[0] // 2, 25), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, vehicle_name, (text_x - text_size_vehicle[0] // 2, 55), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        #cv2.putText(image, id_text, (text_x - text_size_id[0] // 2, 75), font, 1, (255, 255, 255), 1, cv2.LINE_AA) car ID
        
        if self.show_speed_text:
            self.get_vehicle_speed()# Get the vehicle speed
            speed_text = f"{round(self.speed)}"  # Speed text
            text_size_speed = cv2.getTextSize(speed_text, font, 1, 1)[0]
            cv2.putText(image, speed_text, ((text_x - text_size_speed[0] // 2) -47, text_y_start + 225), font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
            #cv2.putText(image, speed_text, self.speed_hud_location[0], self.speed_hud_location[1], font, 0.75, (0, 0, 0), 2, cv2.LINE_AA)

        self.add_icons(image, h, w)

    def add_icons(self,image, height, width):
        """Add icons to the image based on toggle states."""
        poscount = 0
        for icon_name, filename in self.icons.items():
            if getattr(self, f'show_{icon_name}', False):
                icon = cv2.imread(os.path.join(self.icon_path, filename), cv2.IMREAD_UNCHANGED)
                icon = cv2.resize(icon, self.iconscale)  # Resize the icon if needed
                if(icon_name == 'icon_stopwatch'):
                    abs_position = (int(height * self.speed_hud_location[0]), int(width * self.speed_hud_location[1]))
                else:
                    abs_position = (int(height * self.icon_positions[poscount][0]), int(width * self.icon_positions[poscount][1]))
                    poscount=poscount+1
                self.overlay_icon(image, icon, abs_position)

    def overlay_icon(self, image, icon, position):
        """Overlay the icon onto the image at the given position."""
        y, x = position
        h, w = icon.shape[:2]

        if icon.shape[2] == 4:  # Handle transparency
            alpha_s = icon[:, :, 3] / 255.0 *self.hud_alpha
            alpha_l = 1.0 - alpha_s
            for c in range(0, 3):
                image[y:y+h, x:x+w, c] = (alpha_s * icon[:, :, c] + alpha_l * image[y:y+h, x:x+w, c])
        else:
            # If no alpha channel, apply the transparency directly
            for c in range(0, 3):
                image[y:y+h, x:x+w, c] = (self.alpha * icon[:, :, c] + (1 - self.hud_alpha) * image[y:y+h, x:x+w, c])

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
                self.set_xml_config(vehicle)
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
        exit()
    if client:
        client.cleanup()
