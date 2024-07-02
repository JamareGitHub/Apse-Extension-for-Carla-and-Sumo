import tkinter as tk
import subprocess
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
import os
import random
import time
import xml.dom.minidom as minidom

# Basisverzeichnis für CARLA und die Konfigurationsdatei
carla_base_dir = r"C:\Users\wimme\Downloads\CARLA\WindowsNoEditor"
config_script = os.path.join(carla_base_dir, "PythonAPI", "util", "config.py")

# Basisverzeichnis für SUMO
sumo_base_dir = os.path.join(carla_base_dir, "Co-Simulation", "Sumo")

output_folder = r"C:\Users\wimme\Documents\Uni\9. Semester\combined"

# Liste der verfügbaren Maps
maps = {
    "Town01": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town01")),
    "Town04": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town04")),
    "Town05": "{}.sumocfg".format(os.path.join(sumo_base_dir, "examples", "Town05"))
}

hud_count = 0

# Pfad zur vorhandenen XML-Datei mit vType-Elementen
vtypes_xml_path = r"C:\Users\wimme\Downloads\CARLA\WindowsNoEditor\Co-Simulation\Sumo\examples\carlavtypes.rou.xml"

def start_simulation():

    global hud_count

    selected_index = map_list.curselection()

    hudSelection()

    if selected_index:
        selected_map = map_list.get(selected_index[0])
        selected_sumocfg = maps[selected_map]
        # Erstelle die .rou.xml Datei für die Fahrzeuge

        modify_vehicle_routes(selected_map)
        
        

        if simulate_var.get(): # Wenn Checkbox angekreuzt ist

            carla_exe = os.path.join(carla_base_dir, "CarlaUE4.exe")

            try:
                # Starte die CarlaUE4.exe mit dem Argument -dx11
                print("Starte CarlaUE4.exe...")
                subprocess.Popen([carla_exe, "-dx11"])

                # Warte ein paar Sekunden, damit CarlaUE4.exe gestartet werden kann
                time.sleep(20)
                print("Wartezeit nach dem Start von CarlaUE4.exe.")

                # Führe das Konfigurationsskript aus
                print("Starte Konfigurationsskript: {}".format(config_script))
                config_command = ["python", config_script, "--map", selected_map]
                subprocess.Popen(config_command, cwd=os.path.dirname(config_script))

                # Warte kurz vor der Ausführung des nächsten Befehls
                time.sleep(5)
                print("Wartezeit vor dem Start des Synchronisationsskripts.")

                # Führe das Synchronisationsskript aus
                sync_script = os.path.join(sumo_base_dir, "run_synchronization.py")
                print("Starte Synchronisationsskript mit SUMO: {}".format(selected_sumocfg))
                sync_command = ["python", sync_script, selected_sumocfg, "--sumo-gui", "--sync-vehicle-color"]
                subprocess.Popen(sync_command, cwd=os.path.dirname(sync_script))

            except FileNotFoundError as e:
                print("Eine der angegebenen Dateien wurde nicht gefunden:", e)
        else:
            start_sumo(selected_sumocfg)
            print("Simulation nicht gestartet, da die Checkbox nicht angekreuzt ist.")

def hudSelection():
    for hud in hud_frames:
        probability = hud['entry'].get()
        brightness_level = hud['brightness_var'].get()
        information_density = hud['density_var'].get()
        information_relevance = hud['relevance_var'].get()
        fov_selection = hud['fov_var'].get()
        calc_distraction(information_relevance, fov_selection, information_density, brightness_level)

        
        print(f"HUD attributes - Probability: {probability}, Brightness Level: {brightness_level}, Information Density: {information_density}, Information Relevance: {information_relevance}, FoV Selection: {fov_selection}")


def calc_distraction(information_relevance, fov_selection, information_density, brightness_level):

    relevance_value = 0
    fov_value= 0
    density_value = 0
    brightness_value = 0
    
    if information_relevance == "Unwichtig" :
        relevance_value = 4
    elif information_relevance == "Neutral":
        relevance_value = 2
    elif information_relevance == "Wichtig":
        relevance_value = 1
    else: 
        relevance_value = 3

    if fov_selection == "Small" :
        fov_value = 4
    elif fov_selection == "Medium":
        fov_value = 1
    elif fov_selection == "Large":
        fov_value = 3
    else: 
        fov_value = 2    

    if information_density == "Minimum" :
        density_value = 1
    elif information_density == "Moderat":
        density_value = 3
    elif information_density == "Maximum":
        density_value = 5
    else: 
        density_value = 2

    if brightness_level == "Sehr dunkel" :
        brightness_value = 5
    elif brightness_level == "Dunkel":
        brightness_value = 3
    elif brightness_level == "Moderat":
        brightness_value = 2
    elif brightness_level == "Hell":
        brightness_value = 4
    elif brightness_level == "Sehr hell":
        brightness_value = 5     
    else: 
        brightness_value = 2    

    base_distraction = 5

    distraction_level = base_distraction + 0.15 * brightness_value + 0.35 * density_value + 0.35 * relevance_value + 0.15 * fov_value     

    print("The distraction level is: " + str(distraction_level))


def start_sumo(selected_sumocfg):
    try:
        # Starte SUMO mit der ausgewählten Konfigurationsdatei
        subprocess.Popen(['sumo-gui', '-c', selected_sumocfg])
        print(f"SUMO Simulation gestartet mit Konfigurationsdatei: {selected_sumocfg}")
        
    except FileNotFoundError:
        print("SUMO konnte nicht gefunden werden. Stelle sicher, dass der Pfad korrekt ist.")


def modify_vehicle_routes(selected_map):
    original_routes_file = os.path.join(sumo_base_dir, "examples", "rou", selected_map + ".rou.xml")
    vehicle_types = ["vehicle.chevrolet.impala", "vehicle.audi.a2"]

    # XML-Dokument einlesen
    try:
        tree = ET.parse(original_routes_file)
        root = tree.getroot()

        # Fahrzeugtypen zufällig zuweisen
        for vehicle in root.findall('vehicle'):
            vehicle_type = random.choice(vehicle_types)
            vehicle.set('type', vehicle_type)
            print(f"Fahrzeug-ID {vehicle.get('id')} zugewiesener Typ: {vehicle_type}")

        # Geändertes XML-Dokument speichern (Überschreiben der Originaldatei)
        tree.write(original_routes_file, encoding="UTF-8", xml_declaration=True)
        print(f"Modifizierte XML-Datei gespeichert unter: {original_routes_file}")

    except ET.ParseError as e:
        print(f"Fehler beim Parsen der XML-Datei {original_routes_file}: {e}")
    except FileNotFoundError as e:
        print(f"Die Datei {original_routes_file} wurde nicht gefunden: {e}")


# Funktion zum Schließen des Hauptfensters
def close_window():
    root.destroy()

# Funktion zum Hinzufügen eines neuen HUDs
def add_hud():
    global hud_count
    hud_count += 1

    hud_idx = len(hud_frames) + 1
    hud_frame = create_hud_frame(hud_idx)
    hud_frames.append(hud_frame)
    hud_frame['frame'].pack(pady=10, padx=20, ipadx=10, ipady=10, fill="x")
    update_scrollregion()

# Funktion zum Entfernen eines HUDs
def remove_hud(hud_frame):
    global hud_count
    hud_count -= 1

    for hud_idx, hud in enumerate(hud_frames):
        if hud['frame'] == hud_frame:
            hud_frames.remove(hud)
            hud_frame.destroy()
            update_hud_names()
            update_scrollregion()
            break

# Funktion zur Aktualisierung der HUD-Namen nach Entfernen eines HUDs
def update_hud_names():
    for hud_idx, hud_frame in enumerate(hud_frames, start=1):
        hud_frame['header'].configure(text=f"HUD {hud_idx}")

# Funktion zur Erstellung des Frames für ein HUD
def create_hud_frame(hud_number):
    frame = tk.Frame(scrollable_frame, bg="white", bd=2, relief="raised")
    header = tk.Label(frame, text=f"HUD {hud_number}", font=('Helvetica', 12, 'bold'), bg="white")
    header.grid(row=0, column=0, columnspan=3, pady=10, sticky='n')

    label_prob = tk.Label(frame, text="Wahrscheinlichkeit eingeben:", bg="white")
    label_prob.grid(row=1, column=0, pady=5, padx=10, sticky='w')
    entry = tk.Entry(frame, width=15)
    entry.insert(0, "0.5")  
    entry.grid(row=1, column=1, pady=5, padx=10, sticky='w')

    prob_tooltip = ToolTip(entry, "Wahrscheinlichkeit, dass das HUD angezeigt wird.")

    prob_question_button = tk.Button(frame, text="?", command=prob_tooltip.show_tooltip, width=3)
    prob_question_button.grid(row=1, column=2, padx=5)
    prob_question_button.bind("<Enter>", lambda event, tooltip=prob_tooltip: tooltip.show_tooltip())
    prob_question_button.bind("<Leave>", lambda event, tooltip=prob_tooltip: tooltip.hide_tooltip())

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

    remove_button = tk.Button(frame, text="HUD entfernen", command=lambda: remove_hud(frame), bg="#ff6347", fg="white")
    remove_button.grid(row=6, column=0, columnspan=3, pady=10)

    return {
        'frame': frame,
        'header': header,
        'entry': entry,
        'brightness_var': brightness_var,
        'density_var': density_var,
        'relevance_var': relevance_var,
        'fov_var': fov_var
    }

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

# Hauptfenster erstellen
root = tk.Tk()
root.title("SUMO Simulation Launcher")

# Variable für den Status der Checkbox
simulate_var = tk.BooleanVar()
simulate_var.set(False)  # Checkbox standardmäßig nicht angekreuzt

# Label für die Auswahl der Map
map_label = tk.Label(root, text="Wähle eine Map:")
map_label.pack(pady=10)

# Listbox für die Auswahl der Map
map_list = tk.Listbox(root)
for map_name in maps:
    map_list.insert(tk.END, map_name)
map_list.pack()

# Checkbox für die Simulation
simulate_checkbox = tk.Checkbutton(root, text="Co-Simulation mit Carla starten", variable=simulate_var)
simulate_checkbox.pack()

# Fenstergröße und Position festlegen
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Hintergrundfarbe für den Canvas und Scrollbar hinzufügen
canvas = tk.Canvas(root, bg="#f0f0f0")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

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

# Dropdown-Optionen und Farben definieren
brightness_level = ["Sehr dunkel", "Dunkel", "Moderat", "Hell", "Sehr hell"]
information_density = ["Minimum", "Moderat", "Maximum"]
information_relevance = ["Unwichtig", "Neutral", "Wichtig"]
fov = ["Small", "Medium", "Large"]

# Liste für HUD Frames
hud_frames = []

# Funktion aufrufen, um standardmäßig 3 HUDs zu erstellen
def create_default_huds():
    for _ in range(3):
        add_hud()

# Button Frame für die Bedienelemente
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

# Buttons erstellen und einfügen
add_hud_button = tk.Button(button_frame, text="HUD hinzufügen", command=add_hud, bg="#4682b4", fg="white")
add_hud_button.pack(side="left", padx=20)

start_button = tk.Button(root, text="Simulation starten", command=start_simulation, bg="#32cd32", fg="white")
start_button.pack(pady=10)

close_button = tk.Button(root, text="Schließen", command=close_window, bg="#a9a9a9", fg="white")
close_button.pack(pady=10)

# Standard-HUDs erstellen
create_default_huds()

# Hauptloop starten
root.mainloop()
