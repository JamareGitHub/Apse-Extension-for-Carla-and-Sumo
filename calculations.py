import math
import random
import numpy as np

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
    # Normalwert (1.0) in einem Bereich von 0.6 bis 2.0
    normal_value = 1.0
    std_dev = 0.4  # Standardabweichung für die Normalverteilung

    # Berechnung des Einflusses auf den Reaktionszeitwert
    distraction_effect = -0.15 * (distraction_level - 1)  # Negativer Einfluss
    fatigueness_effect = -0.1 * (fatigueness_level - 1)  # Negativer Einfluss
    experience_effect = 0.05 * experience_level  # Positiver Einfluss
    awareness_effect = -0.1 * awareness_level  # Negativer Einfluss
    age_effect = 0.01 * age  # Positiver Einfluss

    # Gesamter Einfluss auf die Reaktionszeit
    total_effect = distraction_effect + fatigueness_effect + experience_effect + awareness_effect + age_effect

    # Berechnung der Reaktionszeit unter Berücksichtigung der Normalverteilung
    react_time = normal_value + total_effect + np.random.normal(0, std_dev)

    # Normierung auf den Bereich von 0.6 bis 2.0
    return max(0.6, min(2.0, react_time))  # Sicherstellen, dass der Wert >= 0.6 und <= 2.0 ist

# Beispielaufruf
result = calc_ReactTime(1.5, 1.2, 0.5, 1.0, 30)
print(f"Berechnete Reaktionszeit: {result:.2f} Sekunden")


def calc_MinGap(distraction_level, fatigueness_level, experience_level, awareness_level):
    # Berechnung des Faktors für die Abweichung vom idealen Mindestabstand
    distraction_effect = -0.3 * (2 ** distraction_level)  # Reduziere den Einfluss von Ablenkung
    fatigueness_effect = -0.4 * (2 ** fatigueness_level)   # Reduziere den Einfluss von Müdigkeit
    experience_effect = 0.5 * experience_level            # Erhöhe den Einfluss von Erfahrung
    awareness_effect = 0.5 * awareness_level               # Erhöhe den Einfluss des Bewusstseins

    min_gap_factor = distraction_effect + fatigueness_effect + experience_effect + awareness_effect

    # Sicherstellen, dass der Faktor zwischen 0.4 und 1.5 liegt
    factor = 1 + min_gap_factor  # 1 ist der neutrale Faktor (kein Einfluss)
    if factor < 0.4:
        factor = 0.4
    elif factor > 1.5:
        factor = 1.5

    return factor


def calc_SpeedAd(information_frequency, fov, distraction_level, fatigueness_level, experience_level, awareness_level):
    fov_mapping = {"small": 1, "medium": 2, "large": 3}
    frequency_mapping = {"minimum": 1, "average": 2, "maximum": 3}
    
    fov_value = fov_mapping.get(fov, 2)
    frequency_value = frequency_mapping.get(information_frequency, 2)

    # Anpassung der Effekte für eine höhere Wahrscheinlichkeit von Werten über 1.0
    distraction_effect = 0.1 * (distraction_level ** 2)  # Geringerer Einfluss von Ablenkung
    fatigueness_effect = -0.2 * (fatigueness_level ** 2)  # Milder negativer Einfluss von Müdigkeit

    experience_effect = 0.2 * experience_level  # Starker positiver Einfluss von Erfahrung
    awareness_effect = -0.2 * awareness_level  # Milder negativer Einfluss von Bewusstsein
    fov_effect = -0.01 * fov_value  # Geringer negativer Einfluss des Sichtfeldes
    frequency_effect = -0.005 * frequency_value  # Geringer negativer Einfluss der Informationsdichte

    speed_ad = distraction_effect + fatigueness_effect + experience_effect + awareness_effect + fov_effect + frequency_effect

    # Normierung auf den Bereich von 0.7 bis 1.8
    min_speed_ad = 0.7
    max_speed_ad = 1.8
    normalized_speed_ad = (speed_ad - (-2)) / (4 - (-2))  # Beispiel für Normierung, -2 bis 4 als Bereich
    scaled_speed_ad = normalized_speed_ad * (max_speed_ad - min_speed_ad) + min_speed_ad

    return max(0.7, min(1.8, scaled_speed_ad))  # Sicherstellen, dass der Wert >= 0.7 und <= 1.8 ist


def calc_MaxSpeed(experience_level, awareness_level):
    # Basiswert um 180, aber Streuung zwischen 140 und 220
    base_speed = 180
    experience_effect = random.uniform(-10, 10) * experience_level  # Zufällige Variation
    awareness_effect = random.uniform(-5, 7) * awareness_level  # Weitere zufällige Variation

    max_speed = base_speed + experience_effect + awareness_effect
    return max(140, min(220, max_speed))  # Sicherstellen, dass der Wert zwischen 140 und 220 liegt

def calc_acceleration(experience_level, awareness_level):
    # Basiswert für die Beschleunigung, zufälliger Wert zwischen 2.5 und 8
    base_acceleration = random.uniform(2.5, 8)
    
    # Effekte basierend auf Erfahrungs- und Bewusstseinsebene
    experience_effect = 0.1 * experience_level  # Kleinerer Einfluss für Streuung
    awareness_effect = 0.1 * awareness_level
    
    acceleration = base_acceleration + experience_effect + awareness_effect
    
    # Sicherstellen, dass die Beschleunigung > 2.5 und <= 8
    return max(2.5, min(8, acceleration))