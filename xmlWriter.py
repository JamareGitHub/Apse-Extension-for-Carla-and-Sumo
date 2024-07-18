import tkinter as tk
import xml.etree.ElementTree as ET
import random
import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom
from dicttoxml import dicttoxml
from xmler import dict2xml
import os

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
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")  # Adjust the indentation level as needed

def writeXML(hud_data):

    xml_path = "hudconfig.xml"
    # Create the root element
    root = ET.Element("Vehicles")

    # Create XML structure
    for vehicle_type, attributes in hud_data.items():
        vehicle_elem = ET.SubElement(root, "Vehicle", type_id=vehicle_type)
        for key, value in attributes.items():
            ET.SubElement(vehicle_elem, key).text = str(value)

    # Pretty print the XML
    xml_str = prettify(root)

    # Write to XML file
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"XML file created successfully at {xml_path}")

def modify_vehicle_routes(selected_map, base_dir, hud_frames):
    original_routes_file = os.path.join(base_dir, "examples", "rou", selected_map + ".rou.xml")

    try:
        # XML-Dokument einlesen
        tree = ET.parse(original_routes_file)
        root = tree.getroot()

        # Liste der HUD-IDs und deren Wahrscheinlichkeiten
        vehicle_types = []
        probabilities = []

        for hud in hud_frames:
            probability = float(hud['entry'].get())  # Wahrscheinlichkeit aus dem Eingabefeld
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