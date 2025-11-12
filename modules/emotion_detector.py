import numpy as np
import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PARALLEL_WORKERS, BATCH_SIZE

vokaturi_lib_path = Path(__file__).parent.parent / "OpenVokaturi-4-0" / "OpenVokaturi-4-0" / "api"
sys.path.insert(0, str(vokaturi_lib_path))

try:
    import Vokaturi
    VOKATURI_AVAILABLE = True
except ImportError:
    VOKATURI_AVAILABLE = False

class EmotionDetector:
    
    def __init__(self):
        self.vokaturi_loaded = False
        
        if VOKATURI_AVAILABLE:
            lib_path = self._get_vokaturi_lib_path()
            if lib_path and os.path.exists(lib_path):
                Vokaturi.load(str(lib_path))
                self.vokaturi_loaded = True
    
    def _get_vokaturi_lib_path(self):
        base_path = Path(__file__).parent.parent / "OpenVokaturi-4-0" / "OpenVokaturi-4-0" / "lib" / "open"
        
        import struct
        if sys.platform == "win32":
            if struct.calcsize("P") == 4:
                lib_file = "win/OpenVokaturi-4-0-win32.dll"
            else:
                lib_file = "win/OpenVokaturi-4-0-win64.dll"
        elif sys.platform == "darwin":
            lib_file = "macos/OpenVokaturi-4-0-mac.dylib"
        else:
            lib_file = "linux/OpenVokaturi-4-0-linux.so"
        
        return base_path / lib_file
    
    def analyze_frame(self, frame, sample_rate):
        if not self.vokaturi_loaded:
            return self._fallback_analysis(frame)
        
        buffer_length = len(frame)
        c_buffer = Vokaturi.float64array(buffer_length)
        
        if frame.dtype == np.int16:
            c_buffer[:] = frame[:] / 32768.0
        elif frame.dtype == np.int32:
            c_buffer[:] = frame[:] / 2147483648.0
        else:
            c_buffer[:] = frame[:]
        
        voice = Vokaturi.Voice(float(sample_rate), buffer_length, 0)
        voice.fill_float64array(buffer_length, c_buffer)
        
        quality = Vokaturi.Quality()
        emotion = Vokaturi.EmotionProbabilities()
        voice.extract(quality, emotion)
        
        voice.destroy()
        
        if quality.valid:
            return {
                'neutral': emotion.neutrality,
                'happy': emotion.happiness,
                'sad': emotion.sadness,
                'angry': emotion.anger,
                'fearful': emotion.fear
            }
        
        return self._fallback_analysis(frame)
    
    def _fallback_analysis(self, frame):
        energy = float(np.sqrt(np.mean(frame ** 2)))
        zcr = float(np.mean(np.abs(np.diff(np.sign(frame)))))
        
        if energy > 0.08:
            if zcr > 0.15:
                return {'neutral': 0.2, 'happy': 0.5, 'sad': 0.1, 'angry': 0.1, 'fearful': 0.1}
            else:
                return {'neutral': 0.2, 'happy': 0.1, 'sad': 0.1, 'angry': 0.4, 'fearful': 0.2}
        elif energy < 0.02:
            return {'neutral': 0.4, 'happy': 0.1, 'sad': 0.3, 'angry': 0.1, 'fearful': 0.1}
        else:
            return {'neutral': 0.6, 'happy': 0.1, 'sad': 0.1, 'angry': 0.1, 'fearful': 0.1}
    
    def batch_analyze(self, frames, sample_rate):
        results = []
        
        if not self.vokaturi_loaded or len(frames) < BATCH_SIZE:
            for frame in frames:
                emotion = self.analyze_frame(frame, sample_rate)
                results.append(emotion)
            return results
        
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            future_to_idx = {
                executor.submit(self.analyze_frame, frame, sample_rate): idx 
                for idx, frame in enumerate(frames)
            }
            
            results = [None] * len(frames)
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()
        
        return results
