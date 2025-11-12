# Moodflo - Meeting Emotion Analysis Platform

A privacy-first emotional intelligence dashboard for team meetings that analyzes voice tone patterns to help leaders understand team mood, energy levels, and engagement.

## Features

- **Real-time Analysis**: Upload meeting recordings and watch metrics update live
- **Emotion Detection**: Analyzes vocal tone to detect workplace-relevant emotions
- **Interactive Dashboard**: Beautiful visualizations with dark/light theme support
- **AI Insights**: GPT-4 powered suggestions for meeting improvement
- **Privacy Protected**: Only analyzes tone patterns - never stores raw audio or content

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Edit `.env` and add your OpenAI API key.

4. Install ffmpeg:
   - **Windows**: Download from ffmpeg.org
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

Run the application:
```bash
streamlit run app.py
```

Upload a meeting video or audio file and watch the analysis unfold in real-time.

## Emotion Categories

- ⚡ **Energised**: High engagement and positive energy
- 🔥 **Stressed/Tense**: Signs of pressure or tension
- 🌫 **Flat/Disengaged**: Low energy or minimal participation
- 💬 **Thoughtful/Constructive**: Calm, reflective communication
- 🌪 **Volatile/Unstable**: Mixed emotions and unpredictable patterns

## Privacy

Moodflo is designed with privacy at its core:
- No speech content is recorded or transcribed
- Only acoustic features (pitch, energy, tone) are analyzed
- Raw audio is processed in memory and immediately discarded
- All analysis is performed locally