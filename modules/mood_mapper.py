import numpy as np
from config import MOODFLO_CATEGORIES

class MoodMapper:
    
    @staticmethod
    def map_emotion_to_category(emotion_dict, energy):
        happy = emotion_dict.get('happy', 0)
        angry = emotion_dict.get('angry', 0)
        fearful = emotion_dict.get('fearful', 0)
        sad = emotion_dict.get('sad', 0)
        neutral = emotion_dict.get('neutral', 0)
        
        if happy > 0.4 and energy > 30:
            return "energised"
        
        if (angry + fearful) > 0.35 or (energy > 40 and angry > 0.25):
            return "stressed"
        
        if neutral > 0.55 and energy < 20:
            return "flat"
        
        if neutral > 0.35 and 20 <= energy <= 45 and sad < 0.25:
            return "thoughtful"
        
        return "volatile"
    
    @staticmethod
    def get_category_distribution(emotion_series, energy_series):
        categories = []
        
        for emotion, energy in zip(emotion_series, energy_series):
            category = MoodMapper.map_emotion_to_category(emotion, energy)
            categories.append(category)
        
        distribution = {}
        for category in set(categories):
            count = categories.count(category)
            distribution[MOODFLO_CATEGORIES[category]] = (count / len(categories)) * 100
        
        return distribution, categories
    
    @staticmethod
    def get_dominant_emotion(distribution):
        if not distribution:
            return MOODFLO_CATEGORIES["thoughtful"]
        return max(distribution.items(), key=lambda x: x[1])[0]
