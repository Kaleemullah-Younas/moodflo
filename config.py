import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AUDIO_SAMPLE_RATE = 16000
FRAME_DURATION = 5.0
HOP_DURATION = 2.5
SILENCE_THRESHOLD = 0.015
ENERGY_SCALE = 100
PARALLEL_WORKERS = 80
BATCH_SIZE = 60

MOODFLO_CATEGORIES = {
    "energised": "⚡ Energised",
    "stressed": "🔥 Stressed/Tense",
    "flat": "🌫 Flat/Disengaged",
    "thoughtful": "💬 Thoughtful/Constructive",
    "volatile": "🌪 Volatile/Unstable"
}

PSYCH_SAFETY_THRESHOLDS = {
    "high_risk": {"silence": 25, "stress": 40, "volatility": 7.5},
    "medium_risk": {"silence": 15, "stress": 30, "volatility": 5.5}
}
