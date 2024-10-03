import tkinter as tk
import subprocess
import xml.etree.ElementTree as ET
from tkinter import messagebox
import os
import random
import time
import calculations
from tkinter import ttk
import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom
from PIL import Image, ImageTk
import traci
import csv
from datetime import datetime
import config

#Base directory of CARLA and the config file
carla_base_dir = config.carla_base_dir
config_script = os.path.join(carla_base_dir, "PythonAPI", "util", "config.py")

# Base directory of Sumo
sumo_base_dir = os.path.join(carla_base_dir, "Co-Simulation", "Sumo")

#List of available maps
maps = {
    "Town01": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town01")),
    "Town04": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town04")),
    "Town05": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town05"))
}

# Dropdown options and colors
brightness_level = ["very dark", "dark", "average", "bright", "very bright"]
information_frequency = ["minimum", "average", "maximum"]
information_relevance = ["unimportant", "neutral", "important"]
fov = ["small", "medium", "large"]

hud_count = 0

# Dictionary to store HUD attributes
hud_data = {}

# global list of all available car types
available_vehicle_types = [
    "vehicle.audi.a2", "vehicle.audi.tt",
    "vehicle.chevrolet.impala", "vehicle.mini.cooper_s", "vehicle.mercedes.coupe",
    "vehicle.bmw.grandtourer", "vehicle.citroen.c3", "vehicle.ford.mustang",
    "vehicle.volkswagen.t2", "vehicle.lincoln.mkz_2017", "vehicle.seat.leon"
]

all_vehicle_types = [
    "vehicle.audi.a2", "vehicle.audi.tt",
    "vehicle.chevrolet.impala", "vehicle.mini.cooper_s", "vehicle.mercedes.coupe",
    "vehicle.bmw.grandtourer", "vehicle.citroen.c3", "vehicle.ford.mustang",
    "vehicle.volkswagen.t2", "vehicle.lincoln.mkz_2017", "vehicle.seat.leon"
]

# path to the xml file containing all vtype elements
vtypes_xml_path = carla_base_dir+r"\Co-Simulation\Sumo\examples\carlavtypes.rou.xml"

base_frame = {
        'header': "Hudless Car",
        'entry': 5,
        'brightness_var': "none",
        'frequency_var': "none",
        'relevance_var': "none",
        'fov_var': "none",
        'vehicle_type': "vehicle.nissan.patrol",
        'hud_id': "999"  # unique id for the HUD
    }

hud_id_mapping = {}

def are_all_fields_valid():
    """Checks whether all input fields are filled out correctly."""
    all_valid = True

    # Example checks for input fields
    for hud_frame in hud_frames:
        entry_value = hud_frame['entry'].get()
        if not validate_integer_input(entry_value):
            hud_frame['entry'].config(bg="red")
            all_valid = False
        else:
            hud_frame['entry'].config(bg="white")

    return all_valid

def run_simulation(map):

    min_gap_mapping = {}

    # loop through all Vehicles in hud_data
    for vehicle_type, data in hud_data.items():
        # get the min_gap for the current vehicle_type
        min_gap = data.get("min_Gap")  # make sure min_gap exists
        # save min_gap to a new dictionary
        min_gap_mapping[vehicle_type] = min_gap

    
    path = os.path.join(sumo_base_dir, "examples", map + ".sumocfg")
    traci.start(["sumo", "-c", path])
    
    simulation_data = []  # list to store the simulation data

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()  # Carry out simulation step

        for vehicle_id in traci.vehicle.getIDList():
            current_min_gap = traci.vehicle.getMinGap(vehicle_id)
            current_speed = traci.vehicle.getSpeed(vehicle_id)
            position = traci.vehicle.getPosition(vehicle_id)  
            acceleration = traci.vehicle.getAcceleration(vehicle_id)
            distance_traveled = traci.vehicle.getDistance(vehicle_id)
            time_loss = traci.vehicle.getTimeLoss(vehicle_id)

            # store data in the list
            simulation_data.append([vehicle_id, current_speed, current_min_gap, position[0], position[1], acceleration, distance_traveled, time_loss])
            
            vehicle_type = vehicle_type_mapping.get(vehicle_id, "unknown")

            min_gap_for_vehicle_type = hud_data.get(vehicle_type, {}).get("min_Gap", 1)

            new_min_gap = max(2.0, (current_speed * 3.6 * 0.5 * min_gap_for_vehicle_type))

            traci.vehicle.setMinGap(vehicle_id, new_min_gap)
    

    traci.close()

    # Store the complete simulation data into a csv file
    save_simulation_data(simulation_data)

# Dictionary for every Vehicle Id to store the corresponding vehicle type
vehicle_type_mapping = {}

def save_simulation_data(simulation_data):
    # check if the data has the correct structure
    if not simulation_data or not isinstance(simulation_data, list):
        print("Keine gültigen Simulationsdaten zum Speichern.")
        return

    # Get current date & time
    now = datetime.now()

    # format date & time
    timestamp = now.strftime("%H-%M-%S_%Y-%m-%d")

    # Example csv file path containing date and time
    csv_filename = f'Simulation_data/simulation_data_{timestamp}.csv'

    # Write data to csv file
    with open(csv_filename, mode='w', newline='') as file:
        fieldnames = ['vehicle_id',
                    'hud_id',
                    'vehicle_type',
                    'position_x',
                    'position_y',
                    'current_speed',
                    'current_min_gap',
                    'acceleration',
                    'distance_traveled',
                    'time_loss',
                    'maxSpeed',
                    'speedFactor',
                    'reactionTime',
                    'fatiguenessLevel',
                    'awarenessLevel',
                    'accelFactor']
        
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for entry in simulation_data:
            # Check if entry is a list with the correct length
            if isinstance(entry, list):
                vehicle_id = entry[0]                # Access first element
                current_speed = entry[1]             # Access second element
                current_min_gap = entry[2]           # Access third element
                position_x = entry[3]                # Access fourth element
                position_y = entry[4]                # Access fifth element
                acceleration = entry[5]
                distance_traveled = entry[6]
                time_loss = entry[7]

                # Get vehicle type based on vehicle id from mapping
                vehicle_type = vehicle_type_mapping.get(vehicle_id, "unknown")
                
                # Get hud id based on vehicle type
                hud_id = hud_id_mapping.get(vehicle_type, "unknown")

                # Get hud data based on vehicle type
                hud_data_for_type = hud_data.get(vehicle_type, {})

                # get specific HUD data
                max_speed = hud_data_for_type.get('max_speed', 'N/A')
                speedFactor = hud_data_for_type.get('speed_factor', 'N/A')
                reactionTime = hud_data_for_type.get('reactTime', 'N/A')
                fatiguenessLevel = hud_data_for_type.get('fatigueness_level', 'N/A')
                awarenessLevel = hud_data_for_type.get('awareness_level', 'N/A')
                accelFactor = hud_data_for_type.get('accel_factor', 'N/A')

                
                # Write a new line into the csv file
                writer.writerow({
                    'vehicle_id': vehicle_id,
                    'hud_id': hud_id,
                    'vehicle_type': vehicle_type,
                    'position_x': position_x,
                    'position_y': position_y,
                    'current_speed': current_speed,
                    'current_min_gap': current_min_gap,
                    'acceleration': acceleration,
                    'distance_traveled': distance_traveled,
                    'time_loss': time_loss,
                    'maxSpeed': max_speed,
                    'speedFactor': speedFactor,
                    'reactionTime': reactionTime,
                    'fatiguenessLevel': fatiguenessLevel,
                    'awarenessLevel': awarenessLevel,
                    'accelFactor': accelFactor
                })

    print("Data saved succesfully!")


string_hud_frames = []

def convert_hudFrames():

    for hud in hud_frames:
        # New dictionary with modified values
        string_hud = {
            'header': str(hud['header'].get()),
            'entry': str(hud['entry'].get()),
            'brightness_var': str(hud['brightness_var'].get()),
            'frequency_var': str(hud['frequency_var'].get()),
            'relevance_var': str(hud['relevance_var'].get()),
            'fov_var': str(hud['fov_var'].get()),
            'vehicle_type': str(hud['vehicle_type'].get()),
            'hud_id': str(hud['hud_id'])
        }
    
        # Add new dictionary to list
        string_hud_frames.append(string_hud)

    print(string_hud_frames)

def map_vehicle_type_to_hud_id():
    for hud in string_hud_frames:
        vehicle_type = hud['vehicle_type']  # Get vehicle type from hud
        hud_id = hud['hud_id']  # Get HUD id
        
        # Add mapping of vehicle_type to hud_id
        hud_id_mapping[vehicle_type] = hud_id

        # Optional: Debugging-message, to confirm mapping was successfully
        print(f"Mapping vehicle_type {vehicle_type} to hud_id {hud_id}")

def start_simulation():
    if not map_list.curselection():
        messagebox.showwarning("No map selected", "Please select a map for the simulation.")
        return
    
    if not are_all_fields_valid():
        messagebox.showwarning("Invalid Inputs", "Please enter valid inputs for all the input fields!")
        return
    
    if hudless_var.get() == False and len(hud_frames) == 0:
        messagebox.showwarning("No simulation data", "Please allow simulation without HUD or create HUDs to simulate.")
        return

    selected_index = map_list.curselection()

    xml_path = r"hudconfig.xml"

    global hud_count

    convert_hudFrames()

    if hudless_var.get():
        string_hud_frames.append(base_frame)
        hud_id_mapping["vehicle.nissan.patrol"] = "999"
        print("BASE CAR EXISTS!")

    map_vehicle_type_to_hud_id()

    hud_data = hudSelection()

    # Update max speed
    update_max_speeds(carla_base_dir + r"\Co-Simulation\Sumo\examples\carlavtypes.rou.xml", hud_data)

    if selected_index:
        selected_map = map_list.get(selected_index[0])
        selected_sumocfg = maps[selected_map]

        writeXML(string_hud_frames)

        # Create the .rou.xml file for the chosen vehicles
        modify_vehicle_routes(selected_map)

        carla_exe = os.path.join(carla_base_dir, "CarlaUE4.exe")

        if spectate_var.get() and simulate_var.get() == False:

            try: 
                print("starting CarlaUE4.exe in headless mode")
                subprocess.Popen([carla_exe, "-RenderOffScreen"])

                # wait a couple seconds for CARLA to boot
                time.sleep(20)
                print("timeout after the start of CarlaUE4.exe.")

                # run the config script
                print("Starte Konfigurationsskript: {}".format(config_script))
                config_command = ["python", config_script, "--map", selected_map]
                configsubprocess = subprocess.Popen(config_command, cwd=os.path.dirname(config_script))
                configsubprocess.wait()
                print("Timeout before the start of the config script subprocess")

                # Start the syncronization scrypt
                sync_script = os.path.join(sumo_base_dir, "run_synchronization.py")
                print("Start syncronization script with SUMO: {}".format(selected_sumocfg))
                sync_command = ["python", sync_script, selected_sumocfg, "--sumo-gui", "--sync-vehicle-color"]
                subprocess.Popen(sync_command, cwd=os.path.dirname(sync_script))
                
                try:
                    print("starting spectator")
                    spectatorpath = "./spectator.py"
                    spectatordir = os.path.dirname(spectatorpath)
                    subprocess.Popen(["python", spectatorpath, spectatordir])
                    print("started spectator")
                except FileNotFoundError as e:
                    print("A required file was not found: ", e)

                run_simulation(selected_map)

            except FileNotFoundError as e:
                print("A required file was not found: ", e)

        elif simulate_var.get():
            carla_exe = os.path.join(carla_base_dir, "CarlaUE4.exe")

            try:
                # Start CarlaUE4.exe with the argument -dx11
                print("Starte CarlaUE4.exe...")
                subprocess.Popen([carla_exe])

                # Timeout for CARLA to start
                time.sleep(20)
                print("timeout after the start of CarlaUE4.exe.")

                # Start the configuration Script
                print("Starte Konfigurationsskript: {}".format(config_script))
                config_command = ["python", config_script, "--map", selected_map]
                configsubprocess = subprocess.Popen(config_command, cwd=os.path.dirname(config_script))
                configsubprocess.wait()
                print("Timeout before the start of the config script subprocess")

                # Start the syncronization scrypt
                sync_script = os.path.join(sumo_base_dir, "run_synchronization.py")
                print("Start syncronization script with SUMO: {}".format(selected_sumocfg))
                sync_command = ["python", sync_script, selected_sumocfg, "--sumo-gui", "--sync-vehicle-color"]
                subprocess.Popen(sync_command, cwd=os.path.dirname(sync_script))

                if spectate_var.get():
                    try:
                        print("starting spectator")
                        spectatorpath = "./spectator.py"
                        spectatordir = os.path.dirname(spectatorpath)
                        subprocess.Popen(["python", spectatorpath, spectatordir])
                        print("started spectator")
                    except FileNotFoundError as e:
                        print("A required file was not found: ", e)

                run_simulation(selected_map)

            except FileNotFoundError as e:
                print("A required file was not found: ", e)

        else:
            start_sumo(selected_sumocfg)
            run_simulation(selected_map)


def hudSelection():
    experience_level = 5
    age = 30

    for hud in string_hud_frames:
        brightness_level = hud['brightness_var']
        information_frequency = hud['frequency_var']
        information_relevance = hud['relevance_var']
        fov_selection = hud['fov_var']
        vehicle_type = hud['vehicle_type']

        distraction_level = calculations.calc_distraction(information_relevance, fov_selection, information_frequency, brightness_level)
        fatigueness_level = calculations.calc_fatigueness(information_relevance, fov_selection, information_frequency)
        awareness_level = calculations.calc_awareness(fov_selection, information_relevance, information_frequency, distraction_level, fatigueness_level)
        reactTime = calculations.calc_ReactTime(distraction_level, fatigueness_level, experience_level, awareness_level, age)
        maxSpeed = calculations.calc_MaxSpeed(experience_level, awareness_level)
        gapFactor = calculations.calc_MinGap(distraction_level, fatigueness_level, experience_level, awareness_level)
        speedFactor = calculations.calc_SpeedAd(information_frequency, fov_selection, distraction_level, fatigueness_level, experience_level, awareness_level)
        accel = calculations.calc_acceleration(experience_level, awareness_level)

        # Store the calculated values in the dictionary
        hud_data[vehicle_type] = {
            'reactTime': reactTime,
            'fatigueness_level': fatigueness_level,
            'awareness_level': awareness_level,
            'max_speed': maxSpeed,
            "min_Gap": gapFactor,
            'vehicle_type': vehicle_type,
            'speed_factor': speedFactor,
            'accel_factor': accel,
            'brightness': brightness_level
        }

    return hud_data


def writeXML(hud_list):
    root = ET.Element("Vehicles")
  
    for hud in hud_list:
        vehicle_type = hud['vehicle_type']
        brightness = hud['brightness_var']
        frequency = hud['frequency_var']
        relevance = hud['relevance_var']
        fov = hud['fov_var']
        hud_name = hud['header']

        vehicle_element = ET.SubElement(root, "Vehicle", type_id=vehicle_type)
        ET.SubElement(vehicle_element, "HUDName").text = hud_name
        ET.SubElement(vehicle_element, "Brightness").text = brightness
        ET.SubElement(vehicle_element, "Frequency").text = frequency
        ET.SubElement(vehicle_element, "Relevance").text = relevance
        ET.SubElement(vehicle_element, "FoV").text = fov

    # Store in an xml file
    tree = ET.ElementTree(root)
    xml_file_path = "hudconfig.xml"
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)

    # Optional: Pretty-Print the xml file
    dom = minidom.parseString(ET.tostring(root))
    pretty_xml_as_string = dom.toprettyxml()
    with open(xml_file_path, "w") as f:
        f.write(pretty_xml_as_string)

    return xml_file_path


def update_max_speeds(xml_file_path, hud_data):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    for vehicle_type, data in hud_data.items():

        if vehicle_type.lower() == "vehicle.nissan.patrol":
            continue

        max_speed = data['max_speed']
        speedFactor = data.get('speed_factor', '')
        reactionTime = data.get('reactTime')
        accelFactor = data.get('accel_factor')

        for vtype_elem in root.findall('vType'):
            vtype_id = vtype_elem.get('id')

            if vtype_id == vehicle_type:
                vtype_elem.set('maxSpeed', str(max_speed))
                vtype_elem.set('speedFactor', str(speedFactor))
                vtype_elem.set('accel', str(accelFactor))

                driverstate_params = vtype_elem.findall("./param[@key='has.driverstate.device']")
                if driverstate_params:
                    driverstate_params[0].set('value', 'true')
                else:
                    driverstate_param1 = ET.SubElement(vtype_elem, 'param')
                    driverstate_param1.set('key', 'has.driverstate.device')
                    driverstate_param1.set('value', 'true')

                reaction_time_params = vtype_elem.findall("./param[@key='actionStepLength']")
                if reaction_time_params:
                    reaction_time_params[0].set('value', str(reactionTime))
                else:
                    driverstate_param2 = ET.SubElement(vtype_elem, 'param')
                    driverstate_param2.set('key', 'actionStepLength')
                    driverstate_param2.set('value', str(reactionTime))

                color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                vtype_elem.set('color', color)

    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")  # Adjust the indentation level as needed

def start_sumo(selected_sumocfg):
    try:
        # Start SUMO with the selected configuration file
        subprocess.Popen(['sumo-gui', '-c', selected_sumocfg])
        print(f"SUMO Simulation startet with config file: {selected_sumocfg}")
        
    except FileNotFoundError:
        print("SUMO was not found. Please make sure that the path is correct")


# Dictionary to store vehicle types based on the vehicle id
vehicle_type_mapping = {}

def modify_vehicle_routes(selected_map):
    original_routes_file = os.path.join(sumo_base_dir, "examples", "rou", selected_map + ".rou.xml")

    try:
        # Read xml file
        tree = ET.parse(original_routes_file)
        root = tree.getroot()

        # List of HUD IDs and their probabilities
        vehicle_types = []
        probabilities = []

        for hud in string_hud_frames:
            probability = int(hud['entry'])  # Probability of the input field
            vehicle_type = hud['vehicle_type']  # Selected vehicle type

            vehicle_types.append(vehicle_type)
            probabilities.append(probability)

        # Assign vehicle type to the vehicles on the route
        for vehicle in root.findall('vehicle'):
            if vehicle_types:
                vehicle_id = vehicle.get('id')

                # Choose vehicle type based on their probability
                vehicle_type = random.choices(vehicle_types, probabilities)[0]  

                # Set vehicle type on the route
                vehicle.set('type', vehicle_type)

                # save vehicle type with the vehicle id
                vehicle_type_mapping[vehicle_id] = vehicle_type

        # write changes to the file
        tree.write(original_routes_file)

    except FileNotFoundError:
        print(f"File {original_routes_file} not found.")

# Function to close the window
def close_window():
    root.destroy()

def add_hud():

    if len(hud_frames) >= len(all_vehicle_types):
        print("No additional objects can be added anymore because there are no more additional objects available")
        messagebox.showwarning("No available IDs.", "There are no more IDs available.")
        return
    
    # Create a HUD without any arguments
    hud_frame = create_hud_frame()

    hud_frames.append(hud_frame)

    vehicle_type = hud_frame['vehicle_type'].get()
    available_vehicle_types.remove(vehicle_type)

    # Show HUD frame in UI
    hud_frame['frame'].pack(pady=10, padx=20, ipadx=10, ipady=10, fill="x")
    update_scrollregion()
    
    print("Added HUD: " + str(len(hud_frames)))

   
def remove_hud(hud_id):
    global hud_frames

    # Search HUD element with given ID in the list
    hud_to_remove = next((hud for hud in hud_frames if hud['hud_id'] == hud_id), None)

    if hud_to_remove:
        vehicle_type = hud_to_remove['vehicle_type'].get()
        available_vehicle_types.append(vehicle_type)
        # Remove the frame of the HUD
        hud_to_remove['frame'].destroy()

        # Remove the HUD element from the list
        hud_frames = [hud for hud in hud_frames if hud['hud_id'] != hud_id]
        
        # Update scroll regions
        update_scrollregion()
    else:
        print(f"No HUD found with ID: {hud_id}")


def on_selection(event):
    dropdown = event.widget
    selected_value = dropdown.get()

    # Find the specific object and update the value
    for i, (label, combobox, previous_value) in enumerate(objects):
        if combobox == dropdown:
            # If a value existed before, add it to the list
            if previous_value not in available_vehicle_types:
                available_vehicle_types.append(previous_value)
                
            # Remove new element from the list
            if selected_value in available_vehicle_types:
                available_vehicle_types.remove(selected_value)
            
            # Update saved values in the object
            objects[i] = (label, combobox, selected_value)
            break

    # Update all dropdown menues
    update_comboboxes()

    reselect_map() 

def update_comboboxes():
    for _, dropdown, _ in objects:
        if dropdown.winfo_exists():  # Check if widget exists
            dropdown['values'] = available_vehicle_types

def validate_integer_input(value):
    """Validates the input as a non-empty and non-0 integer."""
    return value.isdigit() and int(value) > 0

def on_validate_input(value, entry):
    reselect_map() 
    """Callback function for validating the input field."""
    if validate_integer_input(value):
        entry.config(bg="white")  # Set background color to white if valid
    else:
        entry.config(bg="red")  # Set background color to red if invalid
    return True  # Continue to allow additional input

def create_hud_frame():
    # Calculate HUD number based on current number of HUDs
    hud_number = len(hud_frames) + 1

    # Create a frame for the HUD
    frame = tk.Frame(scrollable_frame, bg="white", bd=2, relief="raised")

    # Header for the HUD name (initially set as "HUD X")
    global header_entry
    header_entry = tk.Entry(frame, width=20, font=('Helvetica', 14, 'bold'))
    header_entry.insert(0, f"HUD {hud_number}")
    header_entry.grid(row=0, column=0, pady=10, padx=10, sticky='n')

    # input HUD probablity
    label_prob = tk.Label(frame, text="HUD Probability: ", bg="white", font=('Helvetica', 11))
    label_prob.grid(row=1, column=0, pady=5, padx=10, sticky='w')
    
    probability_var = tk.StringVar()
    probability_entry = tk.Entry(frame, textvariable=probability_var, width=15, font=('Helvetica', 11))

    # Register the validation function
    validate_command = frame.register(lambda value: on_validate_input(value, probability_entry))
    probability_entry.config(validate="key", validatecommand=(validate_command, "%P"))
    probability_entry.insert(0, "1")  # Set initial value to 1
    probability_entry.grid(row=1, column=1, pady=5, padx=10, sticky='w')

    # tooltip probability
    prob_tooltip = ToolTip(probability_entry, "Probability is set in fractions. Please only use integers > 0.")

    # Button for questionmark-tooltip
    prob_question_button = tk.Button(frame, text="?", command=prob_tooltip.show_tooltip, width=3)
    prob_question_button.grid(row=1, column=2, padx=5)
    prob_question_button.bind("<Enter>", lambda event, tooltip=prob_tooltip: tooltip.show_tooltip())
    prob_question_button.bind("<Leave>", lambda event, tooltip=prob_tooltip: tooltip.hide_tooltip())

    # Select brightness
    label_brightness = tk.Label(frame, text="HUD brightness: ", bg="white", font=('Helvetica', 11))
    label_brightness.grid(row=2, column=0, pady=5, padx=10, sticky='w')
    
    brightness_var = tk.StringVar(frame)
    brightness_var.set(brightness_level[2])
    brightness_menu = ttk.Combobox(frame, textvariable=brightness_var, values=brightness_level, state="readonly", font=('Helvetica', 11))
    brightness_menu.current(1)  # set to first available value by default
    brightness_menu.grid(row=2, column=1, pady=5, padx=10, sticky='ew')

    brightness_menu.bind('<<ComboboxSelected>>', on_selection)

    brightness_tooltip = ToolTip(brightness_menu, "Very dark: HUD is very visible.\nVery bright: HUD is almost see-through.")
    
    brightness_question_button = tk.Button(frame, text="?", command=brightness_tooltip.show_tooltip, width=3)
    brightness_question_button.grid(row=2, column=2, padx=5)
    brightness_question_button.bind("<Enter>", lambda event, tooltip=brightness_tooltip: tooltip.show_tooltip())
    brightness_question_button.bind("<Leave>", lambda event, tooltip=brightness_tooltip: tooltip.hide_tooltip())

    # Select information frequency
    label_frequency = tk.Label(frame, text="Information frequency: ", bg="white", font=('Helvetica', 11))
    label_frequency.grid(row=3, column=0, pady=5, padx=10, sticky='w')
    
    frequency_var = tk.StringVar(frame)
    frequency_var.set(information_frequency[1])
    frequency_menu = ttk.Combobox(frame, textvariable=frequency_var, values=information_frequency, state="readonly", font=('Helvetica', 11))
    frequency_menu.current(1)  # set to first available value by default
    frequency_menu.grid(row=3, column=1, pady=5, padx=10, sticky='ew')

    frequency_menu.bind('<<ComboboxSelected>>', on_selection)

    frequency_tooltip = ToolTip(frequency_menu, "Minimum: the information is only displayed when needed\nMaximum: information is always displayed")
    
    frequency_question_button = tk.Button(frame, text="?", command=frequency_tooltip.show_tooltip, width=3)
    frequency_question_button.grid(row=3, column=2, padx=5)
    frequency_question_button.bind("<Enter>", lambda event, tooltip=frequency_tooltip: tooltip.show_tooltip())
    frequency_question_button.bind("<Leave>", lambda event, tooltip=frequency_tooltip: tooltip.hide_tooltip())

    # Select information relevance
    label_relevance = tk.Label(frame, text="Information relevance: ", bg="white", font=('Helvetica', 11))
    label_relevance.grid(row=4, column=0, pady=5, padx=10, sticky='w')
    
    relevance_var = tk.StringVar(frame)
    relevance_var.set(information_relevance[1])
    relevance_menu = ttk.Combobox(frame, textvariable=relevance_var, values=information_relevance, state="readonly", font=('Helvetica', 11))
    relevance_menu.current(1)  # set to first available value by default
    relevance_menu.grid(row=4, column=1, pady=5, padx=10, sticky='ew')

    relevance_menu.bind('<<ComboboxSelected>>', on_selection)

    relevance_tooltip = ToolTip(relevance_menu, "Unimportant: HUD presents important information and information about your media, the weather,...\nImportant: HUD presents only information that is needed like current speed and navigation instructions.")
    
    relevance_question_button = tk.Button(frame, text="?", command=relevance_tooltip.show_tooltip, width=3)
    relevance_question_button.grid(row=4, column=2, padx=5)
    relevance_question_button.bind("<Enter>", lambda event, tooltip=relevance_tooltip: tooltip.show_tooltip())
    relevance_question_button.bind("<Leave>", lambda event, tooltip=relevance_tooltip: tooltip.hide_tooltip())

    # Select Field of View (FoV)
    label_fov = tk.Label(frame, text="Field of View: ", bg="white", font=('Helvetica', 11))
    label_fov.grid(row=5, column=0, pady=5, padx=10, sticky='w')
    
    fov_var = tk.StringVar(frame)
    fov_var.set(fov[1])
    fov_menu = ttk.Combobox(frame, textvariable=fov_var, values=fov, state="readonly", font=('Helvetica', 11))
    fov_menu.current(1)  # set to first available value by default
    fov_menu.grid(row=5, column=1, pady=5, padx=10, sticky='ew')

    fov_menu.bind('<<ComboboxSelected>>', on_selection)

    fov_tooltip = ToolTip(fov_menu, "Small: Information is displayed directly above steering wheel.\nLarge: Information is displayed on whole windshield.")
    
    fov_question_button = tk.Button(frame, text="?", command=fov_tooltip.show_tooltip, width=3)
    fov_question_button.grid(row=5, column=2, padx=5)
    fov_question_button.bind("<Enter>", lambda event, tooltip=fov_tooltip: tooltip.show_tooltip())
    fov_question_button.bind("<Leave>", lambda event, tooltip=fov_tooltip: tooltip.hide_tooltip())

    # Dropdown für Fahrzeugtyp auswählen
    label_vehicle_type = tk.Label(frame, text="Fahrzeugtyp auswählen:", bg="white", font=('Helvetica', 11))
    label_vehicle_type.grid(row=6, column=0, pady=5, padx=10, sticky='w')

    # Calculate the maximum width for the vehicle type option frames
    max_width = max(len(option) for option in available_vehicle_types) + 2  # +2 for some extra margin
    vehicle_type = tk.StringVar(frame)
    vehicle_type_menu = ttk.Combobox(frame, textvariable=vehicle_type, values=available_vehicle_types, state="readonly", font=('Helvetica', 11))
    vehicle_type_menu.current(0)  # set to first available value by default
    vehicle_type_menu.config(width=max_width)  # set width based on widest option
    vehicle_type_menu.grid(row=6, column=1, pady=5, padx=10, sticky='ew')

    vehicle_type_menu.bind('<<ComboboxSelected>>', on_selection)
    
    # Save new object and its initial value (empty)
    objects.append((label_vehicle_type, vehicle_type_menu, vehicle_type.get()))

    # Save HUD object for later
    hud = {
        'frame': frame,
        'header': header_entry,
        'entry': probability_entry,
        'brightness_var': brightness_var,
        'frequency_var': frequency_var,
        'relevance_var': relevance_var,
        'fov_var': fov_var,
        'vehicle_type': vehicle_type,
        'hud_id': hud_number  # Unique ID of the HUD
    }

    # button to remove the HUD
    remove_button = tk.Button(frame, text="Remove HUD", command=lambda: remove_hud(hud.get("hud_id")), bg="#ff6347", fg="white", width=15, font=('Helvetica', 12))  # Schriftgröße anpassen
    remove_button.grid(row=7, column=0, columnspan=3, pady=10)

    # Return hud object for managing
    return hud


objects=[]

def dropdown_opened(dropdown):
    dropdown['values'] = available_vehicle_types  # Update all values of the dropdown menu

def getList():
    return available_vehicle_types

# ToolTip class to create the tooltip window
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 250
        y += self.widget.winfo_rooty() + 20

        # create tooltip window if it doesnt exist
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background='#ffffe0', relief='solid', borderwidth=1,
                         wraplength=200)
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# Function to update the scroll region
def update_scrollregion():
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# function to close the window
def close_window():
    root.quit()

# Function to store the current selection
selected_map_index = None

def on_map_select(event):
    global selected_map_index
    selected_index = map_list.curselection()
    if selected_index:
        selected_map_index = selected_index[0]

def reselect_map():
    if selected_map_index is not None:
        map_list.selection_clear(0, tk.END)  # Remove previous stored selection
        map_list.selection_set(selected_map_index)  # Set the previously saved selection
        map_list.activate(selected_map_index)  # Re-focus the selected map

# Create main window
root = tk.Tk()
root.title("SUMO Simulation Launcher")

# Window size and position
window_width = 800
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Create Tab widget
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Create main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main")

#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#--------------------HELP PAGE------------------------#
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

# Crate help tab
help_tab = ttk.Frame(notebook)
notebook.add(help_tab, text="Help")

# Add background color for Canvas and scrollbar
canvas = tk.Canvas(help_tab, bg="#f0f0f0")
scrollbar = tk.Scrollbar(help_tab, orient="vertical", command=canvas.yview)

# Create scrollable frame
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

# Configure canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Bind mouswheel to scroll event
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Bind canvas to mouswheel
canvas.bind("<MouseWheel>", on_mouse_wheel)

# pack canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Hotkeys for the CARLA Spectator Client", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Here are some hotkeys that you can use to navigate in the CARLA Spectator Client. This won't \n"
                        "work in the CARLA server.\n \n Hotkeys: \n   -q = quit: terminate the spectator client \n   -n = next: Switch to the next vehicle \n"
                        "   -o = overlay: toggle the overlay that shows the name of the HUD and the car \n    (does not toggle the configured HUD!)", font=("Arial", 12), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# empty line
empty_label = tk.Label(scrollable_frame, text="")
empty_label.pack(pady=5, padx=20, anchor="w")  # Padding after the empty line

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Setting a HUD for simulation", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Probability", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="You can use the probability field to change the probability of the specific HUD getting simulated in the \n simulation."
                        "The probability is set in fractions, not percentage! Please make sure to enter an Integer > 0.", font=("Arial", 12), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Brightness", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Additional text on the help tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The brightness level represents how visible the HUD will be for the driver. \n" 
    "The options are: \n"
    "   - very dark \n"
    "   - dark \n"
    "   - average \n"
    "   - bright \n"
    "   - very bright \n"
    "While the option 'very dark' will make the HUD extremely visible, the option 'very bright' makes the \n HUD almost see-through."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Load pictures and resize them
image1 = Image.open("screenshots\\hud-brightness-very-bright.png")
image1 = image1.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image1_tk = ImageTk.PhotoImage(image1)

image2 = Image.open("screenshots\\hud-brightness-very-dark.png")
image2 = image2.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image2_tk = ImageTk.PhotoImage(image2)

# Create frame for pictures and descriptions
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame for Picture 1 and description
frame1 = tk.Frame(image_frame)
frame1.pack(side="left", padx=20)

# Picture 1 and description in frame 1
label_image1 = tk.Label(frame1, image=image1_tk)
label_image1.pack(pady=10)

label_desc1 = tk.Label(frame1, text="Brightness level: 'very bright'", font=("Arial", 12))
label_desc1.pack(pady=10)

# Frame for Picture 2 and description
frame2 = tk.Frame(image_frame)
frame2.pack(side="left", padx=20)

# Picture 2 and description in frame 2
label_image2 = tk.Label(frame2, image=image2_tk)
label_image2.pack(pady=5)

label_desc2 = tk.Label(frame2, text="Brightness level: 'very dark'", font=("Arial", 12))
label_desc2.pack(pady=10)

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Field of View", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Additional text on the help tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The Field of View (FoV) defines the position of the information on the windshield.\n" 
    "The options are: \n"
    "   - small \n"
    "   - medium \n"
    "   - large \n"
    "A large FoV projects elements directly in the driving environment exploiting the size of the whole \n simulated windshield while a small FoV means that items are placed above the steering \n wheel with a fixed location and less space for information presentation."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Load pictures and resize them
image12 = Image.open("screenshots\\hud-fov-small.png")
image12 = image12.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image12_tk = ImageTk.PhotoImage(image12)

image22 = Image.open("screenshots\\hud-fov-large.png")
image22 = image22.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image22_tk = ImageTk.PhotoImage(image22)

# Create frame for pictures and descriptions
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame for Picture 1 and description
frame12 = tk.Frame(image_frame)
frame12.pack(side="left", padx=20)

# Picture 1 and description in frame 1
label_image12 = tk.Label(frame12, image=image12_tk)
label_image12.pack(pady=10)

label_desc12 = tk.Label(frame12, text="FoV: 'small'", font=("Arial", 12))
label_desc12.pack(pady=10)

# Frame for Picture 2 and description
frame22 = tk.Frame(image_frame)
frame22.pack(side="left", padx=20)

# Picture 2 and description in frame 2
label_image22 = tk.Label(frame22, image=image22_tk)
label_image22.pack(pady=5)

label_desc22 = tk.Label(frame22, text="FoV: 'large'", font=("Arial", 12))
label_desc22.pack(pady=10)

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Information relevance", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Additional text on the help tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The information relevance describes the average relevance level of the \n information that is being displayed." 
    "The options are: \n"
    "   - unimportant \n"
    "   - neutral \n"
    "   - important \n"
    "'important' means that only important information like the speed of the driver, the speed limit and navigation \n instruction will be displayed on the HUD while 'unimportant' will also represent \n information about your music player or the temperature outside "
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Load pictures and resize them
image13 = Image.open("screenshots\\hud-relevance-unimportant.png")
image13 = image13.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image13_tk = ImageTk.PhotoImage(image13)

image23 = Image.open("screenshots\\hud-relevance-important.png")
image23 = image23.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image23_tk = ImageTk.PhotoImage(image23)

# Create frame for pictures and descriptions
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame for Picture 1 and description
frame13 = tk.Frame(image_frame)
frame13.pack(side="left", padx=20)

# Picture 1 and description in frame 1
label_image13 = tk.Label(frame13, image=image13_tk)
label_image13.pack(pady=10)

label_desc13 = tk.Label(frame13, text="Information relevance: 'unimportant'", font=("Arial", 12))
label_desc13.pack(pady=10)

# Frame for Picture 2 and description
frame23 = tk.Frame(image_frame)
frame23.pack(side="left", padx=20)

# Picture 2 and description in frame 2
label_image23 = tk.Label(frame23, image=image23_tk)
label_image23.pack(pady=5)

label_desc23 = tk.Label(frame23, text="Information relevance: 'important'", font=("Arial", 12))
label_desc23.pack(pady=10)

# Header on the help tab
header_label = tk.Label(scrollable_frame, text="Information frequency", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Additional text on the help tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The information frequency describes when the information is displayed on the windshield. \n" 
    "The options are: \n"
    "   - minimum \n"
    "   - average \n"
    "   - maximum \n"
    "'minimum' means the information is only being displayed when needed to 'maximum' means all \n available information is always displayed."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Load pictures and resize them
image14 = Image.open("screenshots\\hud-all-min.png")
image14 = image14.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image14_tk = ImageTk.PhotoImage(image14)

image24 = Image.open("screenshots\\hud-all-max.png")
image24 = image24.resize((340, 200), Image.Resampling.LANCZOS)  # Adjust picture size
image24_tk = ImageTk.PhotoImage(image24)

# Create frame for pictures and descriptions
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame for Picture 1 and description
frame14 = tk.Frame(image_frame)
frame14.pack(side="left", padx=20)

# Picture 1 and description in frame 1
label_image14 = tk.Label(frame14, image=image14_tk)
label_image14.pack(pady=10)

label_desc14 = tk.Label(frame14, text="Information frequency: 'minimum'", font=("Arial", 12))
label_desc14.pack(pady=10)

# Frame for Picture 2 and description
frame24 = tk.Frame(image_frame)
frame24.pack(side="left", padx=20)

# Picture 2 and description in frame 2
label_image24 = tk.Label(frame24, image=image24_tk)
label_image24.pack(pady=5)

label_desc24 = tk.Label(frame24, text="Information frequency: 'maximum'", font=("Arial", 12))
label_desc24.pack(pady=10)


# Update the Scroll regions of the canvas
scrollable_frame.update_idletasks()  # Make sure that all tasks are complete
canvas.configure(scrollregion=canvas.bbox("all"))  # Set scroll region after adding content


#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#---------------MAIN PAGE--------------------#
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

# Variable to set the state of the checkbox
simulate_var = tk.BooleanVar()
simulate_var.set(False)  # checkbox not selected by default
spectate_var = tk.BooleanVar()
spectate_var.set(False)  # checkbox not selected by default
hudless_var = tk.BooleanVar()
hudless_var.set(False)

# Label to select the map
map_label = tk.Label(main_tab, text="Wähle eine Map:", font=('Helvetica', 14, 'bold'))
map_label.pack(pady=5)

# list box to select the map
map_list = tk.Listbox(main_tab, font=('Helvetica', 12), height=5, width=10)
for map_name in maps:
    map_list.insert(tk.END, map_name)


map_list.pack(pady=10)

# Bind the selection event to save the map
map_list.bind('<<ListboxSelect>>', on_map_select)


# Checkbox Simulation
simulate_checkbox = tk.Checkbutton(main_tab, text="Start co-Simulation with CARLA", variable=simulate_var, font=('Helvetica', 12))
simulate_checkbox.pack()

# Checkbox spectator
spectator_checkbox = tk.Checkbutton(main_tab, text="Start the CARLA first-person spectator client", variable=spectate_var, font=('Helvetica', 12))
spectator_checkbox.pack()

# Checkbox HUDless car
hudless_checkbox = tk.Checkbutton(main_tab, text="Simulate a car without HUD", variable=hudless_var, font=('Helvetica', 12))
hudless_checkbox.pack()

# Set background color for canvas and scrollbar
canvas = tk.Canvas(main_tab, bg="#f0f0f0")
scrollbar = tk.Scrollbar(main_tab, orient="vertical", command=canvas.yview)

# Create scrollable frame
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

# Canvas configuration
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Bind mouswheel for scrolling
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

# Pack canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# List of hud frames
hud_frames = []

# Call funktion to create 3 huds by dedault
def create_default_huds():
    for _ in range(3):
        add_hud()

# Button frame for the controls
button_frame = tk.Frame(main_tab, bg="#f0f0f0")
button_frame.pack(pady=10)

# Create button and add it
button_width = 20  # width of the buttons
button_height = 2  # Height of the buttons

# Create button and add it
add_hud_button = tk.Button(button_frame, text="Add HUD", command=add_hud, bg="#4682b4", fg="white", width=button_width, height=button_height, font=('Helvetica', 10))
add_hud_button.pack(pady=10)  # pack the button with some top padding

start_button = tk.Button(button_frame, text="Start simulation", command=start_simulation, bg="#32cd32", fg="white", width=button_width, height=button_height, font=('Helvetica', 10))
start_button.pack(pady=10)  # pack the button with some top padding

close_button = tk.Button(button_frame, text="Close", command=close_window, bg="#a9a9a9", fg="white", width=button_width, height=button_height, font=('Helvetica', 10))
close_button.pack(pady=10, padx=10) 
# unbind scrolling over the combobox so that we don't scroll through options (optional)
scrollable_frame.unbind_class("TCombobox", "<MouseWheel>")

# empty antiscroll method
def dontscroll(e):
    return "dontscroll"

# methods to bind the mousewheel to scroll the canvas or not
def on_enter(e):
    scrollable_frame.bind_all("<MouseWheel>", dontscroll)

def _on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

def on_leave(e):
    scrollable_frame.bind_all("<MouseWheel>", _on_mouse_wheel)

# while hovering over a listbox, dont scroll the canvas on mousewheel, otherwise do
scrollable_frame.bind_class('Listbox', '<Enter>', on_enter)
scrollable_frame.bind_class('Listbox', '<Leave>', on_leave)

# create default huds
create_default_huds()

# start main loop
root.mainloop()
