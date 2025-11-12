from openai import OpenAI

class InsightsGenerator:
    
    def __init__(self, api_key=None):
        """Initialize with optional API key. If None, will use fallback suggestions."""
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def generate_suggestions(self, analysis_data):
        if not self.client:
            return self._fallback_suggestions(analysis_data)
        
        prompt = self._build_prompt(analysis_data)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert meeting coach analyzing emotional patterns. Provide 4-5 concise, actionable suggestions based on acoustic analysis. Focus on psychological safety and practical next steps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    
    def _build_prompt(self, data):
        prompt = f"""Meeting Acoustic Analysis Summary:

Dominant Emotion: {data['dominant_emotion']}
Average Energy Level: {data['avg_energy']:.1f}/100
Silence Percentage: {data['silence_pct']:.1f}%
Participation Rate: {data['participation']:.1f}%
Volatility Score: {data['volatility']:.1f}/10
Psychological Safety Risk: {data['psych_risk']}

Emotion Distribution:
"""
        for emotion, percentage in data['distribution'].items():
            prompt += f"- {emotion}: {percentage:.1f}%\n"
        
        prompt += "\nGenerate 4-5 actionable suggestions for the meeting leader."
        return prompt
    
    def _fallback_suggestions(self, data):
        suggestions = []
        dominant = data['dominant_emotion']
        
        # Category-specific detailed suggestions matching user requirements
        if "Energised" in dominant:
            category_header = "⚡ ENERGISED\nTeam is upbeat, vocal, lively. Energy is high.\n"
            suggestions.extend([
                "Let the team finish early (afternoon off) — protect the momentum",
                "Share quick wins publicly — reward the energy",
                "Add buffer time between meetings to cool down",
                "Capture insights and decisions while engagement is peak"
            ])
        elif "Stressed" in dominant or "Tense" in dominant:
            category_header = "🔥 STRESSED / TENSE\nTeam tone is clipped, overlapping, strained. Stress showing.\n"
            suggestions.extend([
                "Cancel the next non-essential meeting",
                "Offer one-to-one check-ins this week",
                "Share one thing that's under control",
                "Consider postponing non-urgent decisions until tension eases"
            ])
        elif "Flat" in dominant or "Disengaged" in dominant:
            category_header = "🌫️ FLAT / DISENGAGED\nTeam is quiet, slow, low tone. Participation is down.\n"
            suggestions.extend([
                "Cut meeting time by 50% next week",
                "End the week early — protect recovery",
                "Give space for feedback anonymously",
                "Introduce interactive elements or smaller breakout discussions"
            ])
        elif "Thoughtful" in dominant or "Constructive" in dominant:
            category_header = "💬 THOUGHTFUL / FOCUSED\nTeam is calm, steady, reflective. This is a healthy signal.\n"
            suggestions.extend([
                "Capture insights while they're fresh",
                "Keep next meeting format identical — this one worked",
                'Ask: "What helped today\'s flow?"',
                "Maintain this collaborative environment in future sessions"
            ])
        elif "Volatile" in dominant or "Unstable" in dominant:
            category_header = "🌪️ VOLATILE / UNSTABLE\nTone is unpredictable, intense, emotionally mixed.\n"
            suggestions.extend([
                "Follow up with 1–2 people who spoke less",
                "Reiterate shared goals in writing",
                "Flag for facilitation support next session",
                "Consider breaking into smaller discussion groups"
            ])
        else:
            category_header = "MEETING ANALYSIS\n"
            suggestions.extend([
                "Review meeting structure and participation patterns",
                "Consider individual check-ins with team members",
                "Monitor emotional patterns in upcoming meetings"
            ])
        
        # Add psychological safety warning if needed
        if data['psych_risk'] == "High":
            psych_header = "\n🧠 PSYCH-SAFETY RISK: HIGH\nSilence + tension detected. Low participation, high volatility.\n"
            psych_suggestions = [
                "⚠️ URGENT: Pause all group decision-making",
                "Ask team to score their current working experience (1–5)",
                "Run a psychological safety retro",
                "Schedule one-to-one's with all team members",
                "Address concerns before proceeding with regular meetings"
            ]
            return category_header + "\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions) + "\n" + psych_header + "\nImmediate Actions:\n" + "\n".join(f"• {s}" for s in psych_suggestions)
        elif data['psych_risk'] == "Medium":
            psych_note = f"\n\n⚠️ PSYCH-SAFETY RISK: MEDIUM\nSilence: {data['silence_pct']:.1f}% | Stress: {data['distribution'].get('🔥 Stressed/Tense', 0):.1f}% | Volatility: {data['volatility']:.1f}\n• Monitor team dynamics closely in next session\n• Consider anonymous feedback channel"
            return category_header + "\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions[:5]) + psych_note
        
        return category_header + "\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions[:5])
