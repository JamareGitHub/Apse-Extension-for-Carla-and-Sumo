import tkinter as tk
import subprocess
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
import os
import random
import time
import xml.dom.minidom as minidom

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
        fov_value = 3
    elif fov_selection == "Medium":
        fov_value = 1
    elif fov_selection == "Large":
        fov_value = 4
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
        brightness_value = 1
    elif brightness_level == "Moderat":
        brightness_value = 2
    elif brightness_level == "Hell":
        brightness_value = 4
    elif brightness_level == "Sehr hell":
        brightness_value = 5     
    else: 
        brightness_value = 2    

    distraction_level =  0.3 * brightness_value + 0.7 * density_value + 0.8* relevance_value + 0.3 * fov_value     

    return int(distraction_level)


def calc_fatigueness(information_relevance, fov_selection, information_density):

    relevance_value = 0
    fov_value= 0
    density_value = 0
    
    if information_relevance == "Unwichtig" :
        relevance_value = 5
    elif information_relevance == "Neutral":
        relevance_value = 3
    elif information_relevance == "Wichtig":
        relevance_value = 1
    else: 
        relevance_value = 3

    if fov_selection == "Small" :
        fov_value = 3
    elif fov_selection == "Medium":
        fov_value = 2
    elif fov_selection == "Large":
        fov_value = 5
    else: 
        fov_value = 2    

    if information_density == "Minimum" :
        density_value = 2
    elif information_density == "Moderat":
        density_value = 3
    elif information_density == "Maximum":
        density_value = 4
    else: 
        density_value = 2

    fatigueness_level = (0.5 * fov_value + 0.8 * relevance_value + 0.7 * density_value) 

    return int(fatigueness_level)


def calc_awareness(fov_selection, information_relevance, information_density, distraction_level, fatigueness_level):

    relevance_value = 0
    fov_value= 0
    density_value = 0
    
    
    if information_relevance == "Unwichtig" :
        relevance_value = 1
    elif information_relevance == "Neutral":
        relevance_value = 2
    elif information_relevance == "Wichtig":
        relevance_value = 4
    else: 
        relevance_value = 3

    if fov_selection == "Small" :
        fov_value = 1
    elif fov_selection == "Medium":
        fov_value = 3
    elif fov_selection == "Large":
        fov_value = 5
    else: 
        fov_value = 2    

    if information_density == "Minimum" :
        density_value = 1
    elif information_density == "Moderat":
        density_value = 5
    elif information_density == "Maximum":
        density_value = 3
    else: 
        density_value = 2
    
    awareness_level = 0.9 * density_value + 0.9 * relevance_value + 0.5 * fov_value + -0.4 * fatigueness_level + -0.3 * distraction_level

    return awareness_level

def calc_ReactTime(distraction_level, fatigueness_level, experience_level, awareness_level, age):

    base_reactTime = 250
    reactTime = base_reactTime + 4 * distraction_level + 3 * fatigueness_level - 1 * experience_level - 4 * awareness_level + 0.1 * age

    return int(reactTime)

def calc_MinGap(distraction_level, fatigueness_level, experience_level, awareness_level):

    minGap = (50 + (-0.6 * distraction_level + -0.9 * fatigueness_level + 0.7 * experience_level + 1 * awareness_level))/10

    return minGap

def calc_SpeedAd(information_density, fov_selection, distraction_level, fatigueness_level, experience_level, awareness_level):

    if fov_selection == "Small" :
        fov_value = 1
    elif fov_selection == "Medium":
        fov_value = 3
    elif fov_selection == "Large":
        fov_value = 5
    else: 
        fov_value = 2    

    if information_density == "Minimum" :
        density_value = 1
    elif information_density == "Moderat":
        density_value = 5
    elif information_density == "Maximum":
        density_value = 3
    else: 
        density_value = 2

    # Berechnung der ursprünglichen Geschwindigkeit
    speedAd = 0.2 * distraction_level - 0.3 * fatigueness_level + 0.1 * experience_level - 0.3 * awareness_level - 0.02 * fov_value - 0.01 * density_value

    # Annahme des Bereichs der ursprünglichen Gleichung (geschätzt aus den Koeffizienten und möglichen Werten)
    min_speedAd = -4
    max_speedAd = 6

    # Normierung des Ergebnisses in den Bereich 0 bis 1
    normalized_speedAd = (speedAd - min_speedAd) / (max_speedAd - min_speedAd)

    # Skalierung und Verschiebung des normierten Ergebnisses in den Bereich 0.7 bis 1.6
    scaled_speedAd = normalized_speedAd * (1.6 - 0.7) + 0.7

    return scaled_speedAd

def calc_LaneChange(fatigueness_level, experience_level, awareness_level):

    laneChange = 1 - 0.1 * fatigueness_level + 0.4 * experience_level + 0.3 * awareness_level

    return laneChange

def calc_MaxSpeed(experience_level, awareness_level):

    laneChange = 120 + 3 * experience_level + 2.5 * awareness_level
    return laneChange