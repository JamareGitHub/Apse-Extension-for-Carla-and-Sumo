import calculations

class HUD:
    def __init__(self, ID, probability, brightness_level, information_density, information_relevance, fov_selection):
        self.ID = ID
        self.probability = probability
        self.brightness_level = brightness_level
        self.information_density = information_density
        self.information_relevance = information_relevance
        self.fov_selection = fov_selection
        self.distraction_level = None
        self.fatigueness_level = None
        self.awareness_level = None
        self.react_time = None
        self.max_speed = None
        self.min_gap = None
        self.speed_factor = None

    def calculate_metrics(self, experience_level, age):
        self.distraction_level = calculations.calc_distraction(self.information_relevance, self.fov_selection, self.information_density, self.brightness_level)
        self.fatigueness_level = calculations.calc_fatigueness(self.information_relevance, self.fov_selection, self.information_density)
        self.awareness_level = calculations.calc_awareness(self.fov_selection, self.information_relevance, self.information_density, self.distraction_level, self.fatigueness_level)
        self.react_time = calculations.calc_ReactTime(self.distraction_level, self.fatigueness_level, experience_level, self.awareness_level, age)
        self.max_speed = calculations.calc_MaxSpeed(experience_level, self.awareness_level)
        self.min_gap = calculations.calc_MinGap(self.distraction_level, self.fatigueness_level, experience_level, self.awareness_level)
        self.speed_factor = calculations.calc_SpeedAd(self.information_density, self.fov_selection, self.distraction_level, self.fatigueness_level, experience_level, self.awareness_level)

    def get_data(self):
        return {
            'reactTime': self.react_time,
            'fatigueness_level': self.fatigueness_level,
            'awareness_level': self.awareness_level,
            'max_speed': self.max_speed,
            'min_Gap': self.min_gap,
            'hud_id': self.ID,
            'speed_factor': self.speed_factor
        }
