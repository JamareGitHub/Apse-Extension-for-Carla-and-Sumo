import tkinter as tk
import subprocess
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
import xml.dom.minidom as minidom

import math

def calc_distraction(information_relevance, fov, information_frequency, brightness_level):
    
    # Einheitliches Mapping
    relevance_mapping = {"unimportant": 1, "neutral": 2, "important": 3}
    fov_mapping = {"small": 1, "medium": 2, "large": 3}
    frequency_mapping = {"minimum": 1, "average": 2, "maximum": 3}
    brightness_mapping = {"very dark": 1, "dark": 2, "average": 3, "bright": 4, "very bright": 5}
    
    relevance_value = relevance_mapping.get(information_relevance, 2)
    fov_value = fov_mapping.get(fov, 2)
    frequency_value = frequency_mapping.get(information_frequency, 2)
    brightness_value = brightness_mapping.get(brightness_level, 3)

    # Quadratische Abhängigkeit von Information Frequency
    frequency_effect = 0.7 * (frequency_value ** 2)
    
    # Logarithmische Abhängigkeit von Brightness Level (flacht bei hohen Werten ab)
    brightness_effect = 0.3 * math.log(brightness_value + 1)
    
    # Linearer Effekt von Relevance und FOV
    relevance_effect = 0.8 * relevance_value
    fov_effect = 0.3 * fov_value

    # Berechnung des Ablenkungslevels
    distraction_level = brightness_effect + frequency_effect + relevance_effect + fov_effect     
    return int(distraction_level)


def calc_fatigueness(information_relevance, fov, information_frequency):
    
    # Einheitliches Mapping
    relevance_mapping = {"unimportant": 1, "neutral": 2, "important": 3}
    fov_mapping = {"small": 1, "medium": 2, "large": 3}
    frequency_mapping = {"minimum": 1, "average": 2, "maximum": 3}
    
    relevance_value = relevance_mapping.get(information_relevance, 2)
    fov_value = fov_mapping.get(fov, 2)
    frequency_value = frequency_mapping.get(information_frequency, 2)

    # Exponentieller Einfluss der Information Relevance (große Unterschiede bei hohen Werten)
    relevance_effect = 0.8 * (2 ** relevance_value)

    # Quadratische Abhängigkeit des FOV (stärkere Zunahme bei größerem Sichtfeld)
    fov_effect = 0.5 * (fov_value ** 2)

    # Linearer Effekt von Information Frequency
    frequency_effect = 0.7 * frequency_value

    # Berechnung des Müdigkeitslevels
    fatigueness_level = fov_effect + relevance_effect + frequency_effect
    return int(fatigueness_level)


def calc_awareness(fov, information_relevance, information_frequency, distraction_level, fatigueness_level):
    
    # Einheitliches Mapping
    relevance_mapping = {"unimportant": 1, "neutral": 2, "important": 3}
    fov_mapping = {"small": 1, "medium": 2, "large": 3}
    frequency_mapping = {"minimum": 1, "average": 2, "maximum": 3}
    
    relevance_value = relevance_mapping.get(information_relevance, 2)
    fov_value = fov_mapping.get(fov, 2)
    frequency_value = frequency_mapping.get(information_frequency, 2)

    # Logarithmische Abhängigkeit von Information Frequency (flacht bei hohen Werten ab)
    frequency_effect = 0.9 * math.log(frequency_value + 1)

    # Exponentieller Einfluss der Information Relevance
    relevance_effect = 0.9 * (2 ** relevance_value)

    # Quadratische Abhängigkeit vom FOV
    fov_effect = 0.5 * (fov_value ** 2)

    # Negative Einflüsse von Müdigkeit und Ablenkung (linear)
    distraction_effect = -0.3 * distraction_level
    fatigueness_effect = -0.4 * fatigueness_level

    # Berechnung des Bewusstseinslevels
    awareness_level = frequency_effect + relevance_effect + fov_effect + fatigueness_effect + distraction_effect
    return awareness_level


def calc_ReactTime(distraction_level, fatigueness_level, experience_level, awareness_level, age):

    base_reactTime = 250
    
    # Nicht-lineare Beziehung zu Ablenkung und Müdigkeit
    distraction_effect = 4 * (distraction_level ** 1.5)  # Erhöht den Einfluss bei hohen Werten
    fatigueness_effect = 3 * (fatigueness_level ** 1.5)
    
    # Linearer Effekt von Erfahrung und Bewusstsein
    experience_effect = -1 * experience_level
    awareness_effect = -4 * awareness_level

    # Linearer Effekt des Alters
    age_effect = 0.1 * age

    reactTime = base_reactTime + distraction_effect + fatigueness_effect + experience_effect + awareness_effect + age_effect
    return int(reactTime)


def calc_MinGap(distraction_level, fatigueness_level, experience_level, awareness_level):
    
    # Exponentieller Effekt von Ablenkung und Müdigkeit (immer positiv)
    distraction_effect = -0.6 * (2 ** distraction_level)
    fatigueness_effect = -0.9 * (2 ** fatigueness_level)

    # Linearer Effekt von Erfahrung und Bewusstsein
    experience_effect = 0.7 * experience_level
    awareness_effect = 1 * awareness_level

    # Basiswert für Mindestabstand
    base_gap = 5  # Ein positiver Basiswert, der als Mindestabstand dient.

    # Berechnung des Mindestabstands mit einem positiven Basiswert
    minGap = base_gap + distraction_effect + fatigueness_effect + experience_effect + awareness_effect

    # Sicherstellen, dass der Mindestabstand immer größer als 0 ist
    if minGap < base_gap:
        minGap = base_gap

    return minGap


def calc_SpeedAd(information_frequency, fov, distraction_level, fatigueness_level, experience_level, awareness_level):
    
    # Einheitliches Mapping
    fov_mapping = {"small": 1, "medium": 2, "large": 3}
    frequency_mapping = {"minimum": 1, "average": 2, "maximum": 3}
    
    fov_value = fov_mapping.get(fov, 2)
    frequency_value = frequency_mapping.get(information_frequency, 2)

    # Quadratische Abhängigkeit von Ablenkung und Müdigkeit
    distraction_effect = 0.2 * (distraction_level ** 2)
    fatigueness_effect = -0.3 * (fatigueness_level ** 2)

    # Linearer Effekt von Erfahrung, Bewusstsein, FOV und Informationsdichte
    experience_effect = 0.1 * experience_level
    awareness_effect = -0.3 * awareness_level
    fov_effect = -0.02 * fov_value
    frequency_effect = -0.01 * frequency_value

    # Berechnung der ursprünglichen Geschwindigkeit
    speedAd = distraction_effect + fatigueness_effect + experience_effect + awareness_effect + fov_effect + frequency_effect

    # Normierung des Ergebnisses
    min_speedAd = -4
    max_speedAd = 6
    normalized_speedAd = (speedAd - min_speedAd) / (max_speedAd - min_speedAd)

    # Skalierung auf den Bereich 0.7 bis 1.6
    scaled_speedAd = normalized_speedAd * (1.6 - 0.7) + 0.7
    return scaled_speedAd


def calc_LaneChange(fatigueness_level, experience_level, awareness_level):

    # Quadratische Abhängigkeit von Müdigkeit
    fatigueness_effect = -0.1 * (fatigueness_level ** 2)

    # Linearer Effekt von Erfahrung und Bewusstsein
    experience_effect = 0.4 * experience_level
    awareness_effect = 0.3 * awareness_level

    laneChange = 1 + fatigueness_effect + experience_effect + awareness_effect
    return laneChange


def calc_MaxSpeed(experience_level, awareness_level):

    # Linearer Effekt von Erfahrung und Bewusstsein
    maxSpeed = 120 + 3 * experience_level + 2.5 * awareness_level
    return maxSpeed
