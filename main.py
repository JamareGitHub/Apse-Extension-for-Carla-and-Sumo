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

# Basisverzeichnis für CARLA und die Konfigurationsdatei
carla_base_dir = config.carla_base_dir
config_script = os.path.join(carla_base_dir, "PythonAPI", "util", "config.py")

# Basisverzeichnis für SUMO
sumo_base_dir = os.path.join(carla_base_dir, "Co-Simulation", "Sumo")

# Liste der verfügbaren Maps
maps = {
    "Town01": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town01")),
    "Town04": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town04")),
    "Town05": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town05"))
}

# Dropdown-Optionen und Farben definieren
brightness_level = ["very dark", "dark", "average", "bright", "very bright"]
information_frequency = ["minimum", "average", "maximum"]
information_relevance = ["unimportant", "neutral", "important"]
fov = ["small", "medium", "large"]

hud_count = 0

# Dictionary to store HUD attributes
hud_data = {}

# Globale Liste der verfügbaren Fahrzeugtypen
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

# Pfad zur vorhandenen XML-Datei mit vType-Elementen
vtypes_xml_path = carla_base_dir+r"\Co-Simulation\Sumo\examples\carlavtypes.rou.xml"

base_frame = {
        'header': "Hudless Car",
        'entry': 5,
        'brightness_var': "none",
        'frequency_var': "none",
        'relevance_var': "none",
        'fov_var': "none",
        'vehicle_type': "vehicle.nissan.patrol",
        'hud_id': "999"  # Eindeutige ID für das HUD
    }

hud_id_mapping = {}

def are_all_fields_valid():
    """Überprüft, ob alle Eingabefelder korrekt ausgefüllt sind."""
    all_valid = True

    # Beispielhafte Überprüfungen für Eingabefelder
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

    # Iteriere durch jedes Fahrzeug in hud_data
    for vehicle_type, data in hud_data.items():
        # Hole den min_Gap für den aktuellen vehicle_type
        min_gap = data.get("min_Gap")  # Stelle sicher, dass min_Gap existiert
        # Speichere den min_Gap im neuen Dictionary
        min_gap_mapping[vehicle_type] = min_gap

    
    path = os.path.join(sumo_base_dir, "examples", map + ".sumocfg")
    traci.start(["sumo", "-c", path])
    
    simulation_data = []  # Liste zur Speicherung der Simulationsdaten

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()  # Simulationsschritt durchführen

        for vehicle_id in traci.vehicle.getIDList():
            current_min_gap = traci.vehicle.getMinGap(vehicle_id)
            current_speed = traci.vehicle.getSpeed(vehicle_id)
            position = traci.vehicle.getPosition(vehicle_id)  
            acceleration = traci.vehicle.getAcceleration(vehicle_id)
            distance_traveled = traci.vehicle.getDistance(vehicle_id)
            time_loss = traci.vehicle.getTimeLoss(vehicle_id)

            # Speichere die Daten in der Liste
            simulation_data.append([vehicle_id, current_speed, current_min_gap, position[0], position[1], acceleration, distance_traveled, time_loss])
            
            vehicle_type = vehicle_type_mapping.get(vehicle_id, "unknown")

            min_gap_for_vehicle_type = hud_data.get(vehicle_type, {}).get("min_Gap", 1)

            new_min_gap = max(2.0, (current_speed * 3.6 * 0.5 * min_gap_for_vehicle_type))

            traci.vehicle.setMinGap(vehicle_id, new_min_gap)
    

    traci.close()

    # Speichere die gesammelten Simulationsdaten in eine CSV-Datei
    save_simulation_data(simulation_data)

# Dictionary für jede Fahrzeug-ID, um den entsprechenden Fahrzeugtyp zu speichern
vehicle_type_mapping = {}

def save_simulation_data(simulation_data):
    # Überprüfe, ob die Daten die erwartete Struktur haben
    if not simulation_data or not isinstance(simulation_data, list):
        print("Keine gültigen Simulationsdaten zum Speichern.")
        return

    # Aktuelles Datum und Uhrzeit erhalten
    now = datetime.now()

    # Formatieren des Datums und der Uhrzeit
    timestamp = now.strftime("%H-%M-%S_%Y-%m-%d")

    # Beispiel-CSV-Dateipfad mit Datum und Uhrzeit
    csv_filename = f'simulation_data_{timestamp}.csv'

    # Schreibe die Daten in die CSV
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
            # Überprüfe, ob entry eine Liste ist und die erwartete Länge hat
            if isinstance(entry, list):
                vehicle_id = entry[0]                # Zugreifen auf das erste Element
                current_speed = entry[1]             # Zugreifen auf das zweite Element
                current_min_gap = entry[2]           # Zugreifen auf das dritte Element
                position_x = entry[3]                # Zugreifen auf das vierte Element
                position_y = entry[4]                # Zugreifen auf das fünfte Element
                acceleration = entry[5]
                distance_traveled = entry[6]
                time_loss = entry[7]

                # Hole den vehicle_type basierend auf der vehicle_id aus dem Mapping
                vehicle_type = vehicle_type_mapping.get(vehicle_id, "unknown")
                
                # Hole die hud_id basierend auf dem Fahrzeugtyp
                hud_id = hud_id_mapping.get(vehicle_type, "unknown")

                # Hole die HUD-Daten basierend auf dem vehicle_type
                hud_data_for_type = hud_data.get(vehicle_type, {})

                # Hole die spezifischen Werte aus dem HUD-Datensatz
                max_speed = hud_data_for_type.get('max_speed', 'N/A')
                speedFactor = hud_data_for_type.get('speed_factor', 'N/A')
                reactionTime = hud_data_for_type.get('reactTime', 'N/A')
                fatiguenessLevel = hud_data_for_type.get('fatigueness_level', 'N/A')
                awarenessLevel = hud_data_for_type.get('awareness_level', 'N/A')
                accelFactor = hud_data_for_type.get('accel_factor', 'N/A')

                
                # Schreibe die Zeile in die CSV
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

    print("Daten erfolgreich gespeichert!")


string_hud_frames = []

def convert_hudFrames():

    for hud in hud_frames:
        # Neues Dictionary für die umgewandelten Werte
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
    
        # Füge das neue Dictionary zur Liste hinzu
        string_hud_frames.append(string_hud)

    print(string_hud_frames)

def map_vehicle_type_to_hud_id():
    for hud in string_hud_frames:
        vehicle_type = hud['vehicle_type']  # Den Fahrzeugtyp des HUDs extrahieren
        hud_id = hud['hud_id']  # Die hud_id extrahieren
        
        # Mapping von vehicle_type zu hud_id hinzufügen
        hud_id_mapping[vehicle_type] = hud_id

        # Optional: Debugging-Ausgabe, um sicherzustellen, dass das Mapping korrekt ist
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

    # Update der maximalen Geschwindigkeiten
    update_max_speeds(carla_base_dir + r"\Co-Simulation\Sumo\examples\carlavtypes.rou.xml", hud_data)

    if selected_index:
        selected_map = map_list.get(selected_index[0])
        selected_sumocfg = maps[selected_map]

        writeXML(string_hud_frames)

        # Erstelle die .rou.xml Datei für die Fahrzeuge
        modify_vehicle_routes(selected_map)

        carla_exe = os.path.join(carla_base_dir, "CarlaUE4.exe")

        if spectate_var.get() and simulate_var.get() == False:
            print("TESTERS")

            try: 
                print("Starte CarlaUE4.exe im Off-Screen-Modus...")
                subprocess.Popen([carla_exe, "-RenderOffScreen"])

                # Warte ein paar Sekunden, damit CarlaUE4.exe gestartet werden kann
                time.sleep(20)
                print("Wartezeit nach dem Start von CarlaUE4.exe.")

                # Führe das Konfigurationsskript aus
                print("Starte Konfigurationsskript: {}".format(config_script))
                config_command = ["python", config_script, "--map", selected_map]
                configsubprocess = subprocess.Popen(config_command, cwd=os.path.dirname(config_script))
                configsubprocess.wait()
                print("Wartezeit vor dem Start des Synchronisationsskripts.")

                # Führe das Synchronisationsskript aus
                sync_script = os.path.join(sumo_base_dir, "run_synchronization.py")
                print("Starte Synchronisationsskript mit SUMO: {}".format(selected_sumocfg))
                sync_command = ["python", sync_script, selected_sumocfg, "--sumo-gui", "--sync-vehicle-color"]
                subprocess.Popen(sync_command, cwd=os.path.dirname(sync_script))
                
                try:
                    print("starting spectator")
                    spectatorpath = "./spectator.py"
                    spectatordir = os.path.dirname(spectatorpath)
                    subprocess.Popen(["python", spectatorpath, spectatordir])
                    print("started spectator")
                except FileNotFoundError as e:
                    print("Eine der angegebenen Dateien wurde nicht gefunden:", e)

                run_simulation(selected_map)

            except FileNotFoundError as e:
                print("Eine der angegebenen Dateien wurde nicht gefunden:", e)

        elif simulate_var.get():
            carla_exe = os.path.join(carla_base_dir, "CarlaUE4.exe")

            try:
                # Starte die CarlaUE4.exe mit dem Argument -dx11
                print("Starte CarlaUE4.exe...")
                subprocess.Popen([carla_exe])

                # Warte ein paar Sekunden, damit CarlaUE4.exe gestartet werden kann
                time.sleep(20)
                print("Wartezeit nach dem Start von CarlaUE4.exe.")

                # Führe das Konfigurationsskript aus
                print("Starte Konfigurationsskript: {}".format(config_script))
                config_command = ["python", config_script, "--map", selected_map]
                configsubprocess = subprocess.Popen(config_command, cwd=os.path.dirname(config_script))
                configsubprocess.wait()
                print("Wartezeit vor dem Start des Synchronisationsskripts.")

                # Führe das Synchronisationsskript aus
                sync_script = os.path.join(sumo_base_dir, "run_synchronization.py")
                print("Starte Synchronisationsskript mit SUMO: {}".format(selected_sumocfg))
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
                        print("Eine der angegebenen Dateien wurde nicht gefunden:", e)

                run_simulation(selected_map)

            except FileNotFoundError as e:
                print("Eine der angegebenen Dateien wurde nicht gefunden:", e)

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

    # In eine XML-Datei schreiben
    tree = ET.ElementTree(root)
    xml_file_path = "hudconfig.xml"
    tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)

    # Optional: Pretty-Print der XML-Datei
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
        # Starte SUMO mit der ausgewählten Konfigurationsdatei
        subprocess.Popen(['sumo-gui', '-c', selected_sumocfg])
        print(f"SUMO Simulation gestartet mit Konfigurationsdatei: {selected_sumocfg}")
        
    except FileNotFoundError:
        print("SUMO konnte nicht gefunden werden. Stelle sicher, dass der Pfad korrekt ist.")


# Dictionary zur Speicherung von Fahrzeugtypen basierend auf ihrer ID
vehicle_type_mapping = {}

def modify_vehicle_routes(selected_map):
    original_routes_file = os.path.join(sumo_base_dir, "examples", "rou", selected_map + ".rou.xml")

    try:
        # XML-Dokument einlesen
        tree = ET.parse(original_routes_file)
        root = tree.getroot()

        # Liste der HUD-IDs und deren Wahrscheinlichkeiten
        vehicle_types = []
        probabilities = []

        for hud in string_hud_frames:
            probability = int(hud['entry'])  # Wahrscheinlichkeit aus dem Eingabefeld
            vehicle_type = hud['vehicle_type']  # Ausgewählter Fahrzeugtyp

            vehicle_types.append(vehicle_type)
            probabilities.append(probability)

        # Fahrzeugtypen den Fahrzeugen in der Route zuweisen
        for vehicle in root.findall('vehicle'):
            if vehicle_types:
                vehicle_id = vehicle.get('id')

                # Wählt basierend auf Wahrscheinlichkeiten einen Fahrzeugtyp aus
                vehicle_type = random.choices(vehicle_types, probabilities)[0]  

                # Fahrzeugtyp in der Route setzen
                vehicle.set('type', vehicle_type)

                # Fahrzeug-ID mit dem Fahrzeugtyp speichern
                vehicle_type_mapping[vehicle_id] = vehicle_type

        # Änderungen in die Datei schreiben
        tree.write(original_routes_file)

    except FileNotFoundError:
        print(f"Datei {original_routes_file} nicht gefunden.")

# Funktion zum Schließen des Hauptfensters
def close_window():
    root.destroy()

def add_hud():

    if len(hud_frames) >= len(all_vehicle_types):
        print("Keine weiteren Objekte können hinzugefügt werden, da keine Optionen mehr verfügbar sind.")
        messagebox.showwarning("Keine verfügbaren IDs", "Es sind keine weiteren HUD-IDs verfügbar.")
        return
    
    # Erstelle das HUD ohne Argument
    hud_frame = create_hud_frame()

    hud_frames.append(hud_frame)

    vehicle_type = hud_frame['vehicle_type'].get()
    available_vehicle_types.remove(vehicle_type)

    # HUD-Frame wird im UI angezeigt
    hud_frame['frame'].pack(pady=10, padx=20, ipadx=10, ipady=10, fill="x")
    update_scrollregion()
    
    print("Added HUD: " + str(len(hud_frames)))

   
def remove_hud(hud_id):
    global hud_frames

    # Suche das HUD-Objekt mit der gegebenen ID in der Liste
    hud_to_remove = next((hud for hud in hud_frames if hud['hud_id'] == hud_id), None)

    if hud_to_remove:
        vehicle_type = hud_to_remove['vehicle_type'].get()
        available_vehicle_types.append(vehicle_type)
        # Entferne das Frame des HUDs
        hud_to_remove['frame'].destroy()

        # Entferne das HUD-Objekt aus der Liste
        hud_frames = [hud for hud in hud_frames if hud['hud_id'] != hud_id]
        
        # Aktualisiere die Scrollregion
        update_scrollregion()
    else:
        print(f"No HUD found with ID: {hud_id}")


def on_selection(event):
    dropdown = event.widget
    selected_value = dropdown.get()

    # Finde das entsprechende Objekt und aktualisiere den gespeicherten Wert
    for i, (label, combobox, previous_value) in enumerate(objects):
        if combobox == dropdown:
            # Wenn ein vorheriger Wert vorhanden war, füge ihn zurück zur Liste hinzu
            if previous_value not in available_vehicle_types:
                available_vehicle_types.append(previous_value)
                
            # Entferne den neuen Wert aus der Liste
            if selected_value in available_vehicle_types:
                available_vehicle_types.remove(selected_value)
            
            # Aktualisiere den gespeicherten Wert im Objekt
            objects[i] = (label, combobox, selected_value)
            break

    # Aktualisiere alle Dropdown-Menüs
    update_comboboxes()

    reselect_map() 

def update_comboboxes():
    for _, dropdown, _ in objects:
        if dropdown.winfo_exists():  # Überprüfen, ob das Widget existiert
            dropdown['values'] = available_vehicle_types

def validate_integer_input(value):
    """Validiert die Eingabe als ganze Zahl, die nicht leer und nicht 0 ist."""
    return value.isdigit() and int(value) > 0

def on_validate_input(value, entry):
    reselect_map() 
    """Callback-Funktion für die Validierung des Eingabefeldes."""
    if validate_integer_input(value):
        entry.config(bg="white")  # Setze die Hintergrundfarbe auf Weiß, wenn gültig
    else:
        entry.config(bg="red")  # Setze die Hintergrundfarbe auf Rot, wenn ungültig
    return True  # Erlaube die Eingabe weiterhin

def create_hud_frame():
    # Berechne die HUD-Nummer basierend auf der Anzahl aktuell vorhandener HUDs
    hud_number = len(hud_frames) + 1

    # Erstelle den Frame für das HUD
    frame = tk.Frame(scrollable_frame, bg="white", bd=2, relief="raised")

    # Header für den HUD-Namen (wird initial als "HUD X" gesetzt)
    global header_entry
    header_entry = tk.Entry(frame, width=20, font=('Helvetica', 14, 'bold'))
    header_entry.insert(0, f"HUD {hud_number}")
    header_entry.grid(row=0, column=0, pady=10, padx=10, sticky='n')

    # Wahrscheinlichkeit eingeben
    label_prob = tk.Label(frame, text="HUD Probability: ", bg="white", font=('Helvetica', 11))
    label_prob.grid(row=1, column=0, pady=5, padx=10, sticky='w')
    
    probability_var = tk.StringVar()
    probability_entry = tk.Entry(frame, textvariable=probability_var, width=15, font=('Helvetica', 11))

    # Register the validation function
    validate_command = frame.register(lambda value: on_validate_input(value, probability_entry))
    probability_entry.config(validate="key", validatecommand=(validate_command, "%P"))
    probability_entry.insert(0, "1")  # Set initial value to 1
    probability_entry.grid(row=1, column=1, pady=5, padx=10, sticky='w')

    # Tooltip für Wahrscheinlichkeit
    prob_tooltip = ToolTip(probability_entry, "Probability is set in fractions. Please only use integers > 0.")

    # Button für Fragezeichen-Tooltip
    prob_question_button = tk.Button(frame, text="?", command=prob_tooltip.show_tooltip, width=3)
    prob_question_button.grid(row=1, column=2, padx=5)
    prob_question_button.bind("<Enter>", lambda event, tooltip=prob_tooltip: tooltip.show_tooltip())
    prob_question_button.bind("<Leave>", lambda event, tooltip=prob_tooltip: tooltip.hide_tooltip())

    # Helligkeit auswählen
    label_brightness = tk.Label(frame, text="HUD brightness: ", bg="white", font=('Helvetica', 11))
    label_brightness.grid(row=2, column=0, pady=5, padx=10, sticky='w')
    
    brightness_var = tk.StringVar(frame)
    brightness_var.set(brightness_level[2])
    brightness_menu = ttk.Combobox(frame, textvariable=brightness_var, values=brightness_level, state="readonly", font=('Helvetica', 11))
    brightness_menu.current(1)  # Setzt standardmäßig den ersten verfügbaren Wert
    brightness_menu.grid(row=2, column=1, pady=5, padx=10, sticky='ew')

    brightness_menu.bind('<<ComboboxSelected>>', on_selection)

    brightness_tooltip = ToolTip(brightness_menu, "Very dark: HUD is very visible.\nVery bright: HUD is almost see-through.")
    
    brightness_question_button = tk.Button(frame, text="?", command=brightness_tooltip.show_tooltip, width=3)
    brightness_question_button.grid(row=2, column=2, padx=5)
    brightness_question_button.bind("<Enter>", lambda event, tooltip=brightness_tooltip: tooltip.show_tooltip())
    brightness_question_button.bind("<Leave>", lambda event, tooltip=brightness_tooltip: tooltip.hide_tooltip())

    # Informationsdichte auswählen
    label_frequency = tk.Label(frame, text="Information frequency: ", bg="white", font=('Helvetica', 11))
    label_frequency.grid(row=3, column=0, pady=5, padx=10, sticky='w')
    
    frequency_var = tk.StringVar(frame)
    frequency_var.set(information_frequency[1])
    frequency_menu = ttk.Combobox(frame, textvariable=frequency_var, values=information_frequency, state="readonly", font=('Helvetica', 11))
    frequency_menu.current(1)  # Setzt standardmäßig den ersten verfügbaren Wert
    frequency_menu.grid(row=3, column=1, pady=5, padx=10, sticky='ew')

    frequency_menu.bind('<<ComboboxSelected>>', on_selection)

    frequency_tooltip = ToolTip(frequency_menu, "Minimum: the information is only displayed when needed\nMaximum: information is always displayed")
    
    frequency_question_button = tk.Button(frame, text="?", command=frequency_tooltip.show_tooltip, width=3)
    frequency_question_button.grid(row=3, column=2, padx=5)
    frequency_question_button.bind("<Enter>", lambda event, tooltip=frequency_tooltip: tooltip.show_tooltip())
    frequency_question_button.bind("<Leave>", lambda event, tooltip=frequency_tooltip: tooltip.hide_tooltip())

    # Informationsrelevanz auswählen
    label_relevance = tk.Label(frame, text="Information relevance: ", bg="white", font=('Helvetica', 11))
    label_relevance.grid(row=4, column=0, pady=5, padx=10, sticky='w')
    
    relevance_var = tk.StringVar(frame)
    relevance_var.set(information_relevance[1])
    relevance_menu = ttk.Combobox(frame, textvariable=relevance_var, values=information_relevance, state="readonly", font=('Helvetica', 11))
    relevance_menu.current(1)  # Setzt standardmäßig den ersten verfügbaren Wert
    relevance_menu.grid(row=4, column=1, pady=5, padx=10, sticky='ew')

    relevance_menu.bind('<<ComboboxSelected>>', on_selection)

    relevance_tooltip = ToolTip(relevance_menu, "Unimportant: HUD presents important information and information about your media, the weather,...\nImportant: HUD presents only information that is needed like current speed and navigation instructions.")
    
    relevance_question_button = tk.Button(frame, text="?", command=relevance_tooltip.show_tooltip, width=3)
    relevance_question_button.grid(row=4, column=2, padx=5)
    relevance_question_button.bind("<Enter>", lambda event, tooltip=relevance_tooltip: tooltip.show_tooltip())
    relevance_question_button.bind("<Leave>", lambda event, tooltip=relevance_tooltip: tooltip.hide_tooltip())

    # Field of View (FoV) auswählen
    label_fov = tk.Label(frame, text="Field of View: ", bg="white", font=('Helvetica', 11))
    label_fov.grid(row=5, column=0, pady=5, padx=10, sticky='w')
    
    fov_var = tk.StringVar(frame)
    fov_var.set(fov[1])
    fov_menu = ttk.Combobox(frame, textvariable=fov_var, values=fov, state="readonly", font=('Helvetica', 11))
    fov_menu.current(1)  # Setzt standardmäßig den ersten verfügbaren Wert
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

    # Berechne die maximale Breite für die Fahrzeugtyp-Optionen
    max_width = max(len(option) for option in available_vehicle_types) + 2  # +2 für etwas Puffer
    vehicle_type = tk.StringVar(frame)
    vehicle_type_menu = ttk.Combobox(frame, textvariable=vehicle_type, values=available_vehicle_types, state="readonly", font=('Helvetica', 11))
    vehicle_type_menu.current(0)  # Setzt standardmäßig den ersten verfügbaren Wert
    vehicle_type_menu.config(width=max_width)  # Setze die Breite basierend auf der längsten Option
    vehicle_type_menu.grid(row=6, column=1, pady=5, padx=10, sticky='ew')

    vehicle_type_menu.bind('<<ComboboxSelected>>', on_selection)
    
    # Speichere das neue Objekt und den initialen Wert (leer)
    objects.append((label_vehicle_type, vehicle_type_menu, vehicle_type.get()))

    # Speichere das HUD-Objekt für spätere Verwaltung
    hud = {
        'frame': frame,
        'header': header_entry,
        'entry': probability_entry,
        'brightness_var': brightness_var,
        'frequency_var': frequency_var,
        'relevance_var': relevance_var,
        'fov_var': fov_var,
        'vehicle_type': vehicle_type,
        'hud_id': hud_number  # Eindeutige ID für das HUD
    }

    # Button zum Entfernen des HUDs
    remove_button = tk.Button(frame, text="HUD entfernen", command=lambda: remove_hud(hud.get("hud_id")), bg="#ff6347", fg="white", width=15, font=('Helvetica', 12))  # Schriftgröße anpassen
    remove_button.grid(row=7, column=0, columnspan=3, pady=10)

    # Rückgabe des HUDs als Objekt zur Verwaltung
    return hud


objects=[]

def dropdown_opened(dropdown):
    dropdown['values'] = available_vehicle_types  # Aktualisiere die Werte des Dropdown-Menüs

def getList():
    return available_vehicle_types

# ToolTip Klasse zur Erstellung der Tooltip-Fenster
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 250
        y += self.widget.winfo_rooty() + 20

        # Erstellt das Tooltip-Fenster, wenn noch nicht vorhanden
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


# Funktion zur Aktualisierung der Scrollregion des Canvas
def update_scrollregion():
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Funktion zum Schließen des Fensters
def close_window():
    root.quit()

# Funktion, um die aktuelle Auswahl zu speichern
selected_map_index = None

def on_map_select(event):
    global selected_map_index
    selected_index = map_list.curselection()
    if selected_index:
        selected_map_index = selected_index[0]

def reselect_map():
    if selected_map_index is not None:
        map_list.selection_clear(0, tk.END)  # Alle bisherigen Auswahl entfernen
        map_list.selection_set(selected_map_index)  # Die zuvor gespeicherte Auswahl wieder setzen
        map_list.activate(selected_map_index)  # Fokus auf die ausgewählte Map setzen

# Hauptfenster erstellen
root = tk.Tk()
root.title("SUMO Simulation Launcher")

# Fenstergröße und Position festlegen
window_width = 800
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Tab-Widget erstellen
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Erstellen des Main Tabs
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main")

#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#--------------------HELP PAGE------------------------#
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

# Erstellen des Hilfe Tabs
help_tab = ttk.Frame(notebook)
notebook.add(help_tab, text="Help")

# Hintergrundfarbe für den Canvas und Scrollbar hinzufügen
canvas = tk.Canvas(help_tab, bg="#f0f0f0")
scrollbar = tk.Scrollbar(help_tab, orient="vertical", command=canvas.yview)

# Scrollable Frame erstellen
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

# Canvas Konfigurationen
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Binden des Mausrads für das Scrollen
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Binde das Scrollen des Mausrads an den Canvas
canvas.bind("<MouseWheel>", on_mouse_wheel)

# Canvas und Scrollbar packen
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Hotkeys for the CARLA Spectator Client", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Here are some hotkeys that you can use to navigate in the CARLA Spectator Client. This won't \n"
                        "work in the CARLA server.\n \n Hotkeys: \n   -q = quit: terminate the spectator client \n   -n = next: Switch to the next vehicle \n"
                        "   -o = overlay: toggle the overlay that shows the name of the HUD and the car \n    (does not toggle the configured HUD!)", font=("Arial", 12), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Leerzeile
empty_label = tk.Label(scrollable_frame, text="")
empty_label.pack(pady=5, padx=20, anchor="w")  # Abstand nach der Leerzeile

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Setting a HUD for simulation", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Probability", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=5, padx=20, anchor="w")

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="You can use the probability field to change the probability of the specific HUD getting simulated in the \n simulation."
                        "The probability is set in fractions, not percentage! Please make sure to enter an Integer > 0.", font=("Arial", 12), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Brightness", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Weiterer Text auf dem Hilfe-Tab ----
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

# Bilder laden und anpassen
image1 = Image.open("screenshots\\hud-brightness-very-bright.png")
image1 = image1.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image1_tk = ImageTk.PhotoImage(image1)

image2 = Image.open("screenshots\\hud-brightness-very-dark.png")
image2 = image2.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image2_tk = ImageTk.PhotoImage(image2)

# Frame für die Bilder und Beschreibungen erstellen
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame für Bild 1 und Beschreibung
frame1 = tk.Frame(image_frame)
frame1.pack(side="left", padx=20)

# Bild 1 und Beschreibung in frame1
label_image1 = tk.Label(frame1, image=image1_tk)
label_image1.pack(pady=10)

label_desc1 = tk.Label(frame1, text="Brightness level: 'very bright'", font=("Arial", 12))
label_desc1.pack(pady=10)

# Frame für Bild 2 und Beschreibung
frame2 = tk.Frame(image_frame)
frame2.pack(side="left", padx=20)

# Bild 2 und Beschreibung in frame2
label_image2 = tk.Label(frame2, image=image2_tk)
label_image2.pack(pady=5)

label_desc2 = tk.Label(frame2, text="Brightness level: 'very dark'", font=("Arial", 12))
label_desc2.pack(pady=10)

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Field of View", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Weiterer Text auf dem Hilfe-Tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The Field of View (FoV) defines the position of the information on the windshield.\n" 
    "The options are: \n"
    "   - small \n"
    "   - medium \n"
    "   - large \n"
    "A large FoV projects elements directly in the driving environment exploiting the size of the whole \n simulated windshield while a small FoV means that items are placed above the steering \n wheel with a fixed location and less space for information presentation."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Bilder laden und anpassen
image12 = Image.open("screenshots\\hud-fov-small.png")
image12 = image12.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image12_tk = ImageTk.PhotoImage(image12)

image22 = Image.open("screenshots\\hud-fov-large.png")
image22 = image22.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image22_tk = ImageTk.PhotoImage(image22)

# Frame für die Bilder und Beschreibungen erstellen
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame für Bild 1 und Beschreibung
frame12 = tk.Frame(image_frame)
frame12.pack(side="left", padx=20)

# Bild 1 und Beschreibung in frame1
label_image12 = tk.Label(frame12, image=image12_tk)
label_image12.pack(pady=10)

label_desc12 = tk.Label(frame12, text="FoV: 'small'", font=("Arial", 12))
label_desc12.pack(pady=10)

# Frame für Bild 2 und Beschreibung
frame22 = tk.Frame(image_frame)
frame22.pack(side="left", padx=20)

# Bild 2 und Beschreibung in frame2
label_image22 = tk.Label(frame22, image=image22_tk)
label_image22.pack(pady=5)

label_desc22 = tk.Label(frame22, text="FoV: 'large'", font=("Arial", 12))
label_desc22.pack(pady=10)

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Information relevance", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Weiterer Text auf dem Hilfe-Tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The information relevance describes the average relevance level of the \n information that is being displayed." 
    "The options are: \n"
    "   - unimportant \n"
    "   - neutral \n"
    "   - important \n"
    "'important' means that only important information like the speed of the driver, the speed limit and navigation \n instruction will be displayed on the HUD while 'unimportant' will also represent \n information about your music player or the temperature outside "
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Bilder laden und anpassen
image13 = Image.open("screenshots\\hud-relevance-unimportant.png")
image13 = image13.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image13_tk = ImageTk.PhotoImage(image13)

image23 = Image.open("screenshots\\hud-relevance-important.png")
image23 = image23.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image23_tk = ImageTk.PhotoImage(image23)

# Frame für die Bilder und Beschreibungen erstellen
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame für Bild 1 und Beschreibung
frame13 = tk.Frame(image_frame)
frame13.pack(side="left", padx=20)

# Bild 1 und Beschreibung in frame1
label_image13 = tk.Label(frame13, image=image13_tk)
label_image13.pack(pady=10)

label_desc13 = tk.Label(frame13, text="Information relevance: 'unimportant'", font=("Arial", 12))
label_desc13.pack(pady=10)

# Frame für Bild 2 und Beschreibung
frame23 = tk.Frame(image_frame)
frame23.pack(side="left", padx=20)

# Bild 2 und Beschreibung in frame2
label_image23 = tk.Label(frame23, image=image23_tk)
label_image23.pack(pady=5)

label_desc23 = tk.Label(frame23, text="Information relevance: 'important'", font=("Arial", 12))
label_desc23.pack(pady=10)

# Überschrift auf dem Hilfe-Tab
header_label = tk.Label(scrollable_frame, text="Information frequency", font=("Arial", 14, "bold"), justify="left")
header_label.pack(pady=10, padx=20, anchor="w")

# ---- Weiterer Text auf dem Hilfe-Tab ----
description_label = tk.Label(scrollable_frame, text=(
    "The information frequency describes when the information is displayed on the windshield. \n" 
    "The options are: \n"
    "   - minimum \n"
    "   - average \n"
    "   - maximum \n"
    "'minimum' means the information is only being displayed when needed to 'maximum' means all \n available information is always displayed."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=20, anchor="w")

# Bilder laden und anpassen
image14 = Image.open("screenshots\\hud-all-min.png")
image14 = image14.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image14_tk = ImageTk.PhotoImage(image14)

image24 = Image.open("screenshots\\hud-all-max.png")
image24 = image24.resize((340, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image24_tk = ImageTk.PhotoImage(image24)

# Frame für die Bilder und Beschreibungen erstellen
image_frame = tk.Frame(scrollable_frame)
image_frame.pack(pady=10, padx=10, anchor="w")

# Frame für Bild 1 und Beschreibung
frame14 = tk.Frame(image_frame)
frame14.pack(side="left", padx=20)

# Bild 1 und Beschreibung in frame1
label_image14 = tk.Label(frame14, image=image14_tk)
label_image14.pack(pady=10)

label_desc14 = tk.Label(frame14, text="Information frequency: 'minimum'", font=("Arial", 12))
label_desc14.pack(pady=10)

# Frame für Bild 2 und Beschreibung
frame24 = tk.Frame(image_frame)
frame24.pack(side="left", padx=20)

# Bild 2 und Beschreibung in frame2
label_image24 = tk.Label(frame24, image=image24_tk)
label_image24.pack(pady=5)

label_desc24 = tk.Label(frame24, text="Information frequency: 'maximum'", font=("Arial", 12))
label_desc24.pack(pady=10)


# Aktualisiere die Scrollregion des Canvas
scrollable_frame.update_idletasks()  # Stelle sicher, dass alle Aufgaben abgeschlossen sind
canvas.configure(scrollregion=canvas.bbox("all"))  # Setze die Scrollregion nach dem Hinzufügen von Inhalten


#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#---------------MAIN PAGE--------------------#
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

# Variable für den Status der Checkbox
simulate_var = tk.BooleanVar()
simulate_var.set(False)  # Checkbox standardmäßig nicht angekreuzt
spectate_var = tk.BooleanVar()
spectate_var.set(False)  # Checkbox standardmäßig nicht angekreuzt
hudless_var = tk.BooleanVar()
hudless_var.set(False)

# Label für die Auswahl der Map
map_label = tk.Label(main_tab, text="Wähle eine Map:", font=('Helvetica', 14, 'bold'))
map_label.pack(pady=5)

# Listbox für die Auswahl der Map
map_list = tk.Listbox(main_tab, font=('Helvetica', 12), height=5, width=10)
for map_name in maps:
    map_list.insert(tk.END, map_name)

# Standardmäßig die erste Map auswählen
if maps:  # Überprüfen, ob die Liste nicht leer ist
    map_list.select_set(0)  # Die erste Map auswählen

map_list.pack(pady=10)

# Binde das Auswahlereignis, um die Map zu speichern
map_list.bind('<<ListboxSelect>>', on_map_select)


# Checkbox für die Simulation
simulate_checkbox = tk.Checkbutton(main_tab, text="Start co-Simulation with CARLA", variable=simulate_var, font=('Helvetica', 12))
simulate_checkbox.pack()

# Checkbox für den spectator
spectator_checkbox = tk.Checkbutton(main_tab, text="Start the CARLA first-person spectator client", variable=spectate_var, font=('Helvetica', 12))
spectator_checkbox.pack()

# Checkbox für den spectator
hudless_checkbox = tk.Checkbutton(main_tab, text="Simulate a car without HUD", variable=hudless_var, font=('Helvetica', 12))
hudless_checkbox.pack()

# Hintergrundfarbe für den Canvas und Scrollbar hinzufügen
canvas = tk.Canvas(main_tab, bg="#f0f0f0")
scrollbar = tk.Scrollbar(main_tab, orient="vertical", command=canvas.yview)

# Scrollable Frame erstellen
scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

# Canvas Konfigurationen
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Binden des Mausrads für das Scrollen
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

# Canvas und Scrollbar packen
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Liste für HUD Frames
hud_frames = []

# Funktion aufrufen, um standardmäßig 3 HUDs zu erstellen
def create_default_huds():
    for _ in range(3):
        add_hud()

# Button Frame für die Bedienelemente
button_frame = tk.Frame(main_tab, bg="#f0f0f0")
button_frame.pack(pady=10)

# Buttons erstellen und einfügen
button_width = 20  # Breite der Buttons festlegen
button_height = 2  # Höhe der Buttons festlegen

# Buttons erstellen und einfügen
add_hud_button = tk.Button(button_frame, text="Add HUD", command=add_hud, bg="#4682b4", fg="white", width=button_width, height=button_height, font=('Helvetica', 10))
add_hud_button.pack(pady=10)  # Packe den Button mit Abstand nach oben

start_button = tk.Button(button_frame, text="Start simulation", command=start_simulation, bg="#32cd32", fg="white", width=button_width, height=button_height, font=('Helvetica', 10))
start_button.pack(pady=10)  # Packe den Button mit Abstand nach oben

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

# Standard-HUDs erstellen
create_default_huds()

# Hauptloop starten
root.mainloop()
