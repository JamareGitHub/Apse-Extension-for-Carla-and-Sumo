# Apse-Extension-for-Carla-and-Sumo

## Requirements / Pre-installation
* [Python 3.10](https://www.python.org/downloads/)
* [Sumo 1.20](https://sumo.dlr.de/docs/Downloads.php)
* [Carla 0.9.15](https://carla.readthedocs.io/en/0.9.15/download/)

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

### Files overview:
        Apse-Extension-for-Carla-and-Sumo
        |---icons : Folder that contains the Icons used as HUD elements in the spectator client 
        |    |---12 icon image files
        |---screenshots : Folder that contains screenshots from the components for use in the docs and help page
        |    |---13 screenshots
        |---setup_files : Folder that contains the path and the files that need to be updated within Carla for the program to run
        |    |---root_folder_of_carla
        |          |---WindowsNoEditor
        |               |---Co-Simulation
        |                    |---Sumo
        |                         |---examples
        |                              |---rou
        |                                   |---Town01.rou.xml : Route file for map Town01, required for vehicles to be simulated in Carla
        |                                   |---Town04.rou.xml : Route file for map Town04, required for vehicles to be simulated in Carla
        |                                   |---Town05.rou.xml : Route file for map Town05, required for vehicles to be simulated in Carla
        |---Simulation_data : Folder that contains all generated simulation data, empty by default.
        |---calculations.py : File that contains all simulation formulas.
        |---config.py : Configuration file that contains the path to the Carla folder.
        |---hudconfig.xml : File that contains the HUD config of the last simulation, used to transfer HUD settings from the main client to the spectator client.
        |---main.py : File that contains the main client, used to start all other components and configure all HUDs.
        |---README.md : Readme that contains a overview over all files and instructions to run the program.
        |---requirements.txt : File that contains the python packages that are used and are not included in the default python installation.
        |---spectator.py : File that contains the spectator client, used to spectate Cars from a driver perspective and show an example HUD based on the HUD configuration.

#### Icon/ images source:

* https://www.svgrepo.com/collection/essential-set-2/


