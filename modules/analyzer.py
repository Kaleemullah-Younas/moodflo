import pandas as pd
from modules.audio_processor import AudioProcessor
from modules.emotion_detector import EmotionDetector
from modules.metrics_processor import MetricsProcessor
from modules.mood_mapper import MoodMapper
from modules.cluster_analyzer import ClusterAnalyzer
from modules.risk_assessor import RiskAssessor
from modules.insights_generator import InsightsGenerator

class MeetingAnalyzer:
    
    def __init__(self, openai_api_key=None):
        """Initialize analyzer with optional OpenAI API key for AI-powered insights."""
        self.audio_processor = AudioProcessor()
        self.emotion_detector = EmotionDetector()
        self.mood_mapper = MoodMapper()
        self.cluster_analyzer = ClusterAnalyzer()
        self.risk_assessor = RiskAssessor()
        self.insights_generator = InsightsGenerator(api_key=openai_api_key)
    
    def analyze(self, file_path, progress_callback=None):
        if progress_callback:
            progress_callback(10, "Processing audio...")
        
        audio_data = self.audio_processor.process_file(file_path)
        frames = audio_data['frames']
        timestamps = audio_data['timestamps']
        sample_rate = audio_data['sample_rate']
        
        if progress_callback:
            progress_callback(30, "Detecting emotions...")
        
        emotion_series = self.emotion_detector.batch_analyze(frames, sample_rate)
        
        if progress_callback:
            progress_callback(50, "Computing metrics...")
        
        full_audio = frames.flatten()
        metrics_proc = MetricsProcessor(sample_rate)
        metrics = metrics_proc.calculate_all_metrics(frames, emotion_series, full_audio)
        
        if progress_callback:
            progress_callback(65, "Mapping to categories...")
        
        distribution, categories = self.mood_mapper.get_category_distribution(
            emotion_series, metrics['energy_timeline']
        )
        dominant_emotion = self.mood_mapper.get_dominant_emotion(distribution)
        
        if progress_callback:
            progress_callback(75, "Analyzing patterns...")
        
        cluster_data = self.cluster_analyzer.analyze(emotion_series, metrics['energy_timeline'])
        
        if progress_callback:
            progress_callback(85, "Assessing risks...")
        
        psych_risk = self.risk_assessor.assess_psychological_safety(metrics, distribution)
        
        timeline_df = pd.DataFrame({
            'time': timestamps,
            'energy': metrics['energy_timeline'],
            'category': categories
        })
        
        analysis_summary = {
            'dominant_emotion': dominant_emotion,
            'avg_energy': metrics['avg_energy'],
            'silence_pct': metrics['silence_percentage'],
            'participation': metrics['participation'],
            'volatility': metrics['volatility'],
            'psych_risk': psych_risk,
            'distribution': distribution
        }
        
        if progress_callback:
            progress_callback(95, "Generating insights...")
        
        suggestions = self.insights_generator.generate_suggestions(analysis_summary)
        
        return {
            'summary': analysis_summary,
            'timeline': timeline_df,
            'clusters': cluster_data,
            'suggestions': suggestions,
            'duration': audio_data['duration']
        }
