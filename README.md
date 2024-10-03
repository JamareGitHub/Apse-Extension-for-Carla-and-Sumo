# Apse-Extension-for-Carla-and-Sumo

## Requirements / Pre-installation
* Python 3.10
* Sumo 1.20
* Carla 0.9.15

## Setup
1. Make sure that all requirements are installed and the PATH variable is correctly set.
2. Clone this repository to a location of your choice.
3. Install python packages using pip ("pip install -r .\requirements.txt").
4. Open "config.py" and setup your carla base path up to the folder "\WindowsNoEditor".
5. Copy content of setup_files into the Carla folder (copy the WindowsNoEditor folder over the one from carla, merge/ overwrite if promted)

## Running the Software
1. Run main.py to access the GUI ("python main.py")
2. In the GUI, select which components u want to run. To use the spectator, the Carla server is required
* If you want to run the spectator client at a later point, make sure you startet the Carla server and run spectator.py

## Keybinds spectator:

* q = Quit: Terminate the Spectator Client.
* n = Next: Switch to the next vehicle
* o = Overlay: Toggle the overlay that shows the name of the HUD and car (does not toggle the configured HUD!).

## Technical

#### Files overview:

* main.py: Contains the menu that configures and starts the software. Is also used to start the other components.
* spectator.py: Contains the code just for the spectator client
* calculations.py: Contains all calculations that translate the HUD settings into behavioral changes
* config.py: Configuration file to setup paths to other components
* hudconfig.xml: Contains the current HUD settings for the simulation
* hudconfig.xsd: Validation file for the created hudconfig.xml
* simulation_data.csv: Contains the data from the simulation

#### Icon/ images source:

* https://www.svgrepo.com/collection/essential-set-2/


