# Apse-Extension-for-Carla-and-Sumo

## Requirements

* Separate Sumo Installation
* Separate Carla Installation (If 3D Word view / First-Person Spectator requested)
* python 3.11 installation and PATH setup

## Setup


1. edit config.py to contain your local path to the carla installation folder "WindowsNoEditor" (See example)
2. Copy content of setup_files into the Carla folder (copy the WindowsNoEditor folder over the one from carla, merge/ overwrite if promted)
3. install pip requirements using pip install -r "requirements.txt"

## Running the Software


1. python main.py
2. in the menu, select which components u want. To use the spectator, the Carla server is required

## Keybinds spectator:

* q = Quit: Terminate the Spectator Client
* n = next: Switch to the next vehicle
* o = overlay: toggle the overlay that shows the name of the HUD (does not toggle the configured HUD!)

## Technical

#### Files overview:

* main.py: contains the menu that configures and starts the software. Is also used to start the other components.
* spectator.py: contains the code just for the spectator client
* calculations.py: contains all calculations that translate the HUD settings into behavioral changes
* hudconfig.xml: contains the current HUD settings for the simulation

#### icon/ images source:

* https://www.svgrepo.com/collection/essential-set-2/


