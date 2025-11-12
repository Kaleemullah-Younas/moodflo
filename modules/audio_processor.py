import numpy as np
import soundfile as sf
import subprocess
import tempfile
import os
from pathlib import Path
from config import AUDIO_SAMPLE_RATE, FRAME_DURATION, HOP_DURATION, SILENCE_THRESHOLD

class AudioProcessor:
    
    def __init__(self, sample_rate=AUDIO_SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.frame_duration = FRAME_DURATION
        self.hop_duration = HOP_DURATION
        
    def extract_audio_from_video(self, video_path):
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "extracted_audio.wav")
        
        command = [
             ffmpeg.get_ffmpeg_exe(),
             '-i', str(video_path),
            '-ac', '1',
            '-ar', str(self.sample_rate),
            '-vn', '-y',
            output_path
        ]
        
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    
    def load_audio(self, file_path):
        audio, sr = sf.read(file_path)
        
        if sr != self.sample_rate:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
        
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
            
        return audio, self.sample_rate
    
    def segment_audio(self, audio):
        win_samples = int(self.frame_duration * self.sample_rate)
        hop_samples = int(self.hop_duration * self.sample_rate)
        
        frames = []
        timestamps = []
        
        for i in range(0, len(audio) - win_samples + 1, hop_samples):
            frame = audio[i:i + win_samples]
            frames.append(frame)
            timestamps.append(i / self.sample_rate)
            
        return np.array(frames), np.array(timestamps)
    
    def compute_rms(self, frame):
        return float(np.sqrt(np.mean(frame ** 2)))
    
    def is_silent(self, frame):
        return self.compute_rms(frame) < SILENCE_THRESHOLD
    
    def process_file(self, file_path):
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            audio_path = self.extract_audio_from_video(file_path)
            audio, sr = self.load_audio(audio_path)
            os.remove(audio_path)
        else:
            audio, sr = self.load_audio(file_path)
        
        frames, timestamps = self.segment_audio(audio)
        
        return {
            'frames': frames,
            'timestamps': timestamps,
            'duration': len(audio) / sr,
            'sample_rate': sr
        }

