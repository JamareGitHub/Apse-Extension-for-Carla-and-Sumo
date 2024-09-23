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

# Basisverzeichnis für CARLA und die Konfigurationsdatei
import config
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
information_density = ["minimum", "average", "maximum"]
information_relevance = ["unimportant", "neutral", "important"]
fov = ["small", "medium", "large"]

hud_count = 0

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
        'header': "header_entry",
        'entry': 0.5,
        'brightness_var': "none",
        'density_var': "none",
        'relevance_var': "none",
        'fov_var': "none",
        'vehicle_type': "",
        'hud_id': 999  # Eindeutige ID für das HUD
    }

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
        
    
    # Füge hier weitere spezifische Validierungslogik hinzu, falls nötig

    return all_valid

def start_simulation():
    if not map_list.curselection():
        messagebox.showwarning("No map selected", "Please select a map for the simulation.")
        return
    
    if not are_all_fields_valid():
        print("Ein oder mehrere Felder sind ungültig.")
        messagebox.showwarning("Invalid Inputs", "Please enter valid inputs for all the input fields!")
        return

    selected_index = map_list.curselection()

    xml_path = r"hudconfig.xml"

    global hud_count

    hud_data = hudSelection()
    # xml_data = XML_selection()
        
    print("Gespeicherte HUD-Daten:")
    for vehicle_type in hud_data.items():
       print(f"{vehicle_type}")

    update_max_speeds(carla_base_dir+r"\Co-Simulation\Sumo\examples\carlavtypes.rou.xml", hud_data)

    if hudless_var.get():
        print("BASE CAR EXISTS!")

    if selected_index:
        selected_map = map_list.get(selected_index[0])
        selected_sumocfg = maps[selected_map]

        writeXML(hud_frames)

        # Erstelle die .rou.xml Datei für die Fahrzeuge
        modify_vehicle_routes(selected_map)
    
        if simulate_var.get():  # Wenn Checkbox angekreuzt ist
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
                syncprocess = subprocess.Popen(sync_command, cwd=os.path.dirname(sync_script))

            except FileNotFoundError as e:
                print("Eine der angegebenen Dateien wurde nicht gefunden:", e)
        else:
            start_sumo(selected_sumocfg)
            print("Simulation nicht gestartet, da die Checkbox nicht angekreuzt ist.")

        if spectate_var.get():
            try:
                print("starting spectator")
                spectatorpath = "./spectator.py"
                spectatordir = os.path.dirname(spectatorpath)
                subprocess.Popen(["python", spectatorpath, spectatordir])
                print("started spectator")
            
            except FileNotFoundError as e:
                print("Eine der angegebenen Dateien wurde nicht gefunden:", e)
            

def hudSelection():
    experience_level = 5
    age = 30

    # Dictionary to store HUD attributes
    hud_data = {}

    if hudless_var.get():
        hud_data["vehicle.nissan.patrol"] = {
            'reactTime': 23,
            'fatigueness_level': 1,
            'awareness_level': 1,
            'max_speed': 160,
            "min_Gap": 5,
            'vehicle_type': "vehicle.nissan.patrol",
            'speed_factor': 1,
            'brightness' : "none"
        }

    for hud in hud_frames:
        #probability = hud['entry'].get()
        brightness_level = hud['brightness_var'].get()
        information_density = hud['density_var'].get()
        information_relevance = hud['relevance_var'].get()
        fov_selection = hud['fov_var'].get()
        vehicle_type = hud['vehicle_type'].get()

        distraction_level = calculations.calc_distraction(information_relevance, fov_selection, information_density, brightness_level)
        fatigueness_level = calculations.calc_fatigueness(information_relevance, fov_selection, information_density)
        awareness_level = calculations.calc_awareness(fov_selection, information_relevance, information_density, distraction_level, fatigueness_level)
        reactTime = calculations.calc_ReactTime(distraction_level, fatigueness_level, experience_level, awareness_level, age)
        maxSpeed = calculations.calc_MaxSpeed(experience_level, awareness_level)
        minGap = calculations.calc_MinGap(distraction_level, fatigueness_level, experience_level, awareness_level)
        speedFactor = calculations.calc_SpeedAd(information_density, fov_selection, distraction_level, fatigueness_level, experience_level, awareness_level)


        # Store the calculated values in the dictionary
        hud_data[vehicle_type] = {
            'reactTime': reactTime,
            'fatigueness_level': fatigueness_level,
            'awareness_level': awareness_level,
            'max_speed': maxSpeed,
            "min_Gap": minGap,
            'vehicle_type': vehicle_type,
            'speed_factor': speedFactor,
            'brightness' : brightness_level
        }

    return hud_data


def writeXML(hud_frames):
    """
    Diese Funktion extrahiert die Daten aus den hud_frames und speichert sie in einer XML-Datei.
    :param hud_frames: Liste von Frames, die die HUD-Eingabewerte der Fahrzeuge enthält.
    """
    root = ET.Element("Vehicles")

    if hudless_var.get():
        vehicle_type = "vehicle.nissan.patrol"
        brightness = "none"
        density = "none"
        relevance = "none"
        fov = "none"
        hud_name = "No HUD"

        # Erstelle das XML-Element für das Fahrzeug
        vehicle_element = ET.SubElement(root, "Vehicle", type_id=vehicle_type)
        ET.SubElement(vehicle_element, "HUDName").text = hud_name
        ET.SubElement(vehicle_element, "Brightness").text = brightness
        ET.SubElement(vehicle_element, "Density").text = density
        ET.SubElement(vehicle_element, "Relevance").text = relevance
        ET.SubElement(vehicle_element, "FoV").text = fov
        
    
    # Iteriere durch die HUD-Frames und hole die Werte
    for hud in hud_frames:
        print("Test")
        vehicle_type = hud['vehicle_type'].get()  # Fahrzeugtyp aus dem Entry-Widget
        brightness = hud['brightness_var'].get()  # Helligkeit aus dem Entry-Widget
        density = hud['density_var'].get()  # Dichte aus dem Entry-Widget
        relevance = hud['relevance_var'].get()  # Relevanz aus dem Entry-Widget
        fov = hud['fov_var'].get()  # Sichtfeld aus dem Entry-Widget
        hud_name = hud['header'].get()  # Holt den aktuellen Text


        # Erstelle das XML-Element für das Fahrzeug
        vehicle_element = ET.SubElement(root, "Vehicle", type_id=vehicle_type)
        ET.SubElement(vehicle_element, "HUDName").text = hud_name
        ET.SubElement(vehicle_element, "Brightness").text = brightness
        ET.SubElement(vehicle_element, "Density").text = density
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
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Update maxSpeed, minGapLat, speedFactor, and add driverstate params for each HUD in hud_data
    for vehicle_type, data in hud_data.items():
        max_speed = data['max_speed']
        minGap = data.get('min_Gap', '')  # Assuming 'min_Gap' might not always be present
        speedFactor = data.get('speed_factor', '')  # Assuming 'speed_factor' might not always be present
        reactionTime = data.get('reactTime')

        # Find the vType element with the specified hud_id
        
        for vtype_elem in root.findall('vType'):
            vtype_id = vtype_elem.get('id')

            # Check if the vType id matches the current vehicle_type
            if vtype_id == vehicle_type:
                # Update the maxSpeed, minGapLat, speedFactor attributes
                vtype_elem.set('maxSpeed', str(max_speed))
                vtype_elem.set('minGap', str(minGap))
                vtype_elem.set('speedFactor', str(speedFactor))

                # Check if driverstate params already exist, and update or create accordingly
                driverstate_params = vtype_elem.findall("./param[@key='has.driverstate.device']")
                if driverstate_params:
                    # Update existing param
                    driverstate_params[0].set('value', 'true')
                else:
                    # Create new param
                    driverstate_param1 = ET.SubElement(vtype_elem, 'param')
                    driverstate_param1.set('key', 'has.driverstate.device')
                    driverstate_param1.set('value', 'true')

                # Check and update or create maximalReactionTime param
                reaction_time_params = vtype_elem.findall("./param[@key='maximalReactionTime']")
                if reaction_time_params:
                    # Update existing param
                    reaction_time_params[0].set('value', str(reactionTime))
                else:
                    # Create new param
                    driverstate_param2 = ET.SubElement(vtype_elem, 'param')
                    driverstate_param2.set('key', 'maximalReactionTime')
                    driverstate_param2.set('value', str(reactionTime))

                # Set random color (RGB)
                color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                vtype_elem.set('color', color)

    # Write the updated XML back to the file
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


def modify_vehicle_routes(selected_map):
    original_routes_file = os.path.join(sumo_base_dir, "examples", "rou", selected_map + ".rou.xml")

    try:
        # XML-Dokument einlesen
        tree = ET.parse(original_routes_file)
        root = tree.getroot()

        # Liste der HUD-IDs und deren Wahrscheinlichkeiten
        vehicle_types = []
        probabilities = []

        if hudless_var.get():
            vehicle_types.append("vehicle.nissan.patrol")
            probabilities.append(5)

            
        for hud in hud_frames:
            probability = int(hud['entry'].get())  # Wahrscheinlichkeit aus dem Eingabefeld
            vehicle_type = hud['vehicle_type'].get()  # Ausgewählter Fahrzeugtyp

            vehicle_types.append(vehicle_type)
            probabilities.append(probability)

        # Fahrzeugtypen den Fahrzeugen in der Route zuweisen
        for vehicle in root.findall('vehicle'):
            if vehicle_types:
                vehicle_type = random.choices(vehicle_types, probabilities)[0]  # Wählt basierend auf Wahrscheinlichkeiten aus
                vehicle.set('type', vehicle_type)

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
    
    # Debug-Ausgabe der objects-Liste
    print("Objects before loop:")
    for obj in objects:
        print(obj)

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
    
    # Debug-Ausgabe der objects-Liste nach der Schleife
    print("Objects after loop:")
    for obj in objects:
        print(obj)
    
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
    header_entry.grid(row=0, column=0, pady=10, sticky='n')

    # Wahrscheinlichkeit eingeben
    label_prob = tk.Label(frame, text="Wahrscheinlichkeit eingeben:", bg="white")
    label_prob.grid(row=1, column=0, pady=5, padx=10, sticky='w')
    
    probability_var = tk.StringVar()
    probability_entry = tk.Entry(frame, textvariable=probability_var, width=15)

    # Register the validation function
    validate_command = frame.register(lambda value: on_validate_input(value, probability_entry))
    probability_entry.config(validate="key", validatecommand=(validate_command, "%P"))
    probability_entry.insert(0, "1")  # Set initial value to 1
    probability_entry.grid(row=1, column=1, pady=5, padx=10, sticky='w')

    # Tooltip für Wahrscheinlichkeit
    prob_tooltip = ToolTip(probability_entry, "Wahrscheinlichkeit, dass das HUD angezeigt wird.")

    # Button für Fragezeichen-Tooltip
    prob_question_button = tk.Button(frame, text="?", command=prob_tooltip.show_tooltip, width=3)
    prob_question_button.grid(row=1, column=2, padx=5)
    prob_question_button.bind("<Enter>", lambda event, tooltip=prob_tooltip: tooltip.show_tooltip())
    prob_question_button.bind("<Leave>", lambda event, tooltip=prob_tooltip: tooltip.hide_tooltip())

    # Helligkeit auswählen
    label_brightness = tk.Label(frame, text="Helligkeitsniveau auswählen:", bg="white")
    label_brightness.grid(row=2, column=0, pady=5, padx=10, sticky='w')
    
    brightness_var = tk.StringVar(frame)
    brightness_var.set(brightness_level[2])
    brightness_menu = tk.OptionMenu(frame, brightness_var, *brightness_level)
    brightness_menu.grid(row=2, column=1, pady=5, padx=10, sticky='w')

    brightness_tooltip = ToolTip(brightness_menu, "Helligkeitsniveau des HUDs.")
    
    brightness_question_button = tk.Button(frame, text="?", command=brightness_tooltip.show_tooltip, width=3)
    brightness_question_button.grid(row=2, column=2, padx=5)
    brightness_question_button.bind("<Enter>", lambda event, tooltip=brightness_tooltip: tooltip.show_tooltip())
    brightness_question_button.bind("<Leave>", lambda event, tooltip=brightness_tooltip: tooltip.hide_tooltip())

    # Informationsdichte auswählen
    label_density = tk.Label(frame, text="Informationsdichte für HUD auswählen:", bg="white")
    label_density.grid(row=3, column=0, pady=5, padx=10, sticky='w')
    
    density_var = tk.StringVar(frame)
    density_var.set(information_density[1])
    density_menu = tk.OptionMenu(frame, density_var, *information_density)
    density_menu.grid(row=3, column=1, pady=5, padx=10, sticky='w')

    density_tooltip = ToolTip(density_menu, "Informationsdichte des HUDs.")
    
    density_question_button = tk.Button(frame, text="?", command=density_tooltip.show_tooltip, width=3)
    density_question_button.grid(row=3, column=2, padx=5)
    density_question_button.bind("<Enter>", lambda event, tooltip=density_tooltip: tooltip.show_tooltip())
    density_question_button.bind("<Leave>", lambda event, tooltip=density_tooltip: tooltip.hide_tooltip())

    # Informationsrelevanz auswählen
    label_relevance = tk.Label(frame, text="Informationsrelevanz für HUD auswählen:", bg="white")
    label_relevance.grid(row=4, column=0, pady=5, padx=10, sticky='w')
    
    relevance_var = tk.StringVar(frame)
    relevance_var.set(information_relevance[1])
    relevance_menu = tk.OptionMenu(frame, relevance_var, *information_relevance)
    relevance_menu.grid(row=4, column=1, pady=5, padx=10, sticky='w')

    relevance_tooltip = ToolTip(relevance_menu, "Informationsrelevanz des HUDs.")
    
    relevance_question_button = tk.Button(frame, text="?", command=relevance_tooltip.show_tooltip, width=3)
    relevance_question_button.grid(row=4, column=2, padx=5)
    relevance_question_button.bind("<Enter>", lambda event, tooltip=relevance_tooltip: tooltip.show_tooltip())
    relevance_question_button.bind("<Leave>", lambda event, tooltip=relevance_tooltip: tooltip.hide_tooltip())

    # Field of View (FoV) auswählen
    label_fov = tk.Label(frame, text="Field of View für HUD auswählen:", bg="white")
    label_fov.grid(row=5, column=0, pady=5, padx=10, sticky='w')
    
    fov_var = tk.StringVar(frame)
    fov_var.set(fov[1])
    fov_menu = tk.OptionMenu(frame, fov_var, *fov)
    fov_menu.grid(row=5, column=1, pady=5, padx=10, sticky='w')

    fov_tooltip = ToolTip(fov_menu, "FoV des HUDs.")
    
    fov_question_button = tk.Button(frame, text="?", command=fov_tooltip.show_tooltip, width=3)
    fov_question_button.grid(row=5, column=2, padx=5)
    fov_question_button.bind("<Enter>", lambda event, tooltip=fov_tooltip: tooltip.show_tooltip())
    fov_question_button.bind("<Leave>", lambda event, tooltip=fov_tooltip: tooltip.hide_tooltip())

    # Dropdown für Fahrzeugtyp auswählen
    label_vehicle_type = tk.Label(frame, text="Fahrzeugtyp auswählen:", bg="white")
    label_vehicle_type.grid(row=6, column=0, pady=5, padx=10, sticky='w')
    
    vehicle_type = tk.StringVar(frame)
    vehicle_type_menu = ttk.Combobox(frame, textvariable=vehicle_type, values=available_vehicle_types, state="readonly", postcommand=lambda: dropdown_opened(vehicle_type_menu))
    vehicle_type_menu.current(0)  # Setzt standardmäßig den ersten verfügbaren Wert
    vehicle_type_menu.grid(row=6, column=1, pady=5, padx=10, sticky='w')

    vehicle_type_menu.bind('<<ComboboxSelected>>', on_selection)
    

    # Speichere das neue Objekt und den initialen Wert (leer)
    objects.append((label_vehicle_type, vehicle_type_menu, vehicle_type.get()))

    # Speichere das HUD-Objekt für spätere Verwaltung
    hud = {
        'frame': frame,
        'header': header_entry,
        'entry': probability_entry,
        'brightness_var': brightness_var,
        'density_var': density_var,
        'relevance_var': relevance_var,
        'fov_var': fov_var,
        'vehicle_type': vehicle_type,
        'hud_id': hud_number  # Eindeutige ID für das HUD
    }

    # Button zum Entfernen des HUDs
    remove_button = tk.Button(frame, text="HUD entfernen", command=lambda: remove_hud(hud.get("hud_id")), bg="#ff6347", fg="white")
    remove_button.grid(row=7, column=0, columnspan=3, pady=10)

    # Rückgabe des HUDs als Objekt zur Verwaltung
    return hud

objects=[]

def dropdown_opened(dropdown):
    print("Das Dropdown-Menü wurde geöffnet!")
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
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

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
window_height = 600
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

# Erstellen des Hilfe Tabs
help_tab = ttk.Frame(notebook)
notebook.add(help_tab, text="Help")

help_text = tk.Label(help_tab, text="This is the help tab. Here you can find explanations for the different HUD variables.", font=("Arial", 12), justify="left")
help_text.pack(pady=10, padx=10)

# ---- Überschrift auf dem Hilfe-Tab ----
header_label = tk.Label(help_tab, text="Brightness", font=("Arial", 14, "bold"), justify="center")
header_label.pack(pady=10)

# ---- Weiterer Text auf dem Hilfe-Tab ----
description_label = tk.Label(help_tab, text=(
    "The brightness level represents how visible the HUD will be for the driver. \n" 
    "While the option 'very dark' will make the HUD extremly visible, \n"
    "the option 'very bright' makes the HUD almost see-through."
), font=("Arial", 12), justify="left")
description_label.pack(pady=10, padx=10)

# Bilder laden und anpassen
image1 = Image.open("7498864.png")
image1 = image1.resize((200, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image1_tk = ImageTk.PhotoImage(image1)

image2 = Image.open("7498864.png")
image2 = image2.resize((200, 200), Image.Resampling.LANCZOS)  # Bildgröße anpassen
image2_tk = ImageTk.PhotoImage(image2)

# Frame für die Bilder und Beschreibungen erstellen
frame = tk.Frame(help_tab)
frame.pack(pady=20)

# Bild 1 und Bildbeschreibung hinzufügen
label_image1 = tk.Label(frame, image=image1_tk)
label_image1.grid(row=0, column=0, padx=10)

label_desc1 = tk.Label(frame, text="Brightness level: 'Very dark'")
label_desc1.grid(row=1, column=0, padx=10, pady=5)

# Bild 2 und Bildbeschreibung hinzufügen
label_image2 = tk.Label(frame, image=image2_tk)
label_image2.grid(row=0, column=1, padx=10)

label_desc2 = tk.Label(frame, text="Brightness level: 'Very bright'")
label_desc2.grid(row=1, column=1, padx=10, pady=5)

# Variable für den Status der Checkbox
simulate_var = tk.BooleanVar()
simulate_var.set(False)  # Checkbox standardmäßig nicht angekreuzt
spectate_var = tk.BooleanVar()
spectate_var.set(False)  # Checkbox standardmäßig nicht angekreuzt
hudless_var = tk.BooleanVar()
hudless_var.set(False)

# Label für die Auswahl der Map
map_label = tk.Label(main_tab, text="Wähle eine Map:")
map_label.pack(pady=10)

# Listbox für die Auswahl der Map
map_list = tk.Listbox(main_tab)
for map_name in maps:
    map_list.insert(tk.END, map_name)
map_list.pack()

# Binde das Auswahlereignis, um die Map zu speichern
map_list.bind('<<ListboxSelect>>', on_map_select)

# Checkbox für die Simulation
simulate_checkbox = tk.Checkbutton(main_tab, text="Co-Simulation mit Carla starten", variable=simulate_var)
simulate_checkbox.pack()

# Checkbox für den spectator
spectator_checkbox = tk.Checkbutton(main_tab, text="first person spectator starten", variable=spectate_var)
spectator_checkbox.pack()

# Checkbox für den spectator
hudless_checkbox = tk.Checkbutton(main_tab, text="Simulate a car without HUD", variable=hudless_var)
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
add_hud_button = tk.Button(button_frame, text="HUD hinzufügen", command=add_hud, bg="#4682b4", fg="white")
add_hud_button.pack(side="left", padx=20)

start_button = tk.Button(main_tab, text="Simulation starten", command=start_simulation, bg="#32cd32", fg="white")
start_button.pack(pady=10)

close_button = tk.Button(main_tab, text="Schließen", command=close_window, bg="#a9a9a9", fg="white")
close_button.pack(pady=10)

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