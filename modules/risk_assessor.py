from config import PSYCH_SAFETY_THRESHOLDS

class RiskAssessor:
    
    @staticmethod
    def assess_psychological_safety(metrics, distribution):
        risk_score = 0
        
        silence = metrics['silence_percentage']
        participation = metrics['participation']
        volatility = metrics['volatility']
        
        stress_pct = 0
        for emotion, pct in distribution.items():
            if "Stressed" in emotion or "Tense" in emotion:
                stress_pct = pct
                break
        
        if silence > PSYCH_SAFETY_THRESHOLDS['high_risk']['silence']:
            risk_score += 3
        elif silence > PSYCH_SAFETY_THRESHOLDS['medium_risk']['silence']:
            risk_score += 1
        
        if stress_pct > PSYCH_SAFETY_THRESHOLDS['high_risk']['stress']:
            risk_score += 3
        elif stress_pct > PSYCH_SAFETY_THRESHOLDS['medium_risk']['stress']:
            risk_score += 1
        
        if volatility > PSYCH_SAFETY_THRESHOLDS['high_risk']['volatility']:
            risk_score += 2
        elif volatility > PSYCH_SAFETY_THRESHOLDS['medium_risk']['volatility']:
            risk_score += 1
        
        if participation < 40:
            risk_score += 2
        
        if risk_score >= 5:
            return "High"
        elif risk_score >= 2:
            return "Medium"
        else:
            return "Low"
