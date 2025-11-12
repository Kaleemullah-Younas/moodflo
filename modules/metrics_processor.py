import numpy as np
import librosa
from config import ENERGY_SCALE

class MetricsProcessor:
    
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
    
    def compute_energy(self, frame):
        rms = np.sqrt(np.mean(frame ** 2))
        return float(min(rms * ENERGY_SCALE * 2.5, ENERGY_SCALE))
    
    def detect_silence(self, frames, threshold=0.015):
        silent_count = sum(1 for frame in frames if np.sqrt(np.mean(frame ** 2)) < threshold)
        return (silent_count / len(frames)) * 100 if frames.size > 0 else 0
    
    def estimate_tempo(self, audio):
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]
        return float(tempo)
    
    def compute_participation(self, frames, threshold=0.02):
        active_frames = sum(1 for frame in frames if np.sqrt(np.mean(frame ** 2)) > threshold)
        participation = (active_frames / len(frames)) * 100 if len(frames) > 0 else 0
        return float(participation)
    
    def compute_volatility(self, emotion_series):
        if len(emotion_series) < 2:
            return 0.0
        
        dominant_emotions = []
        for emotions in emotion_series:
            max_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            emotion_map = {'neutral': 0, 'happy': 1, 'sad': 2, 'angry': 3, 'fearful': 4}
            dominant_emotions.append(emotion_map.get(max_emotion, 0))
        
        changes = np.abs(np.diff(dominant_emotions))
        volatility = float(np.mean(changes) * 2.5)
        return min(volatility, 10.0)
    
    def calculate_all_metrics(self, frames, emotion_series, full_audio):
        energy_values = [self.compute_energy(frame) for frame in frames]
        
        metrics = {
            'avg_energy': float(np.mean(energy_values)),
            'silence_percentage': self.detect_silence(frames),
            'participation': self.compute_participation(frames),
            'volatility': self.compute_volatility(emotion_series),
            'tempo': self.estimate_tempo(full_audio),
            'energy_timeline': energy_values
        }
        
        return metrics
