from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io

class ReportGenerator:
    def __init__(self, results, summary, timeline_df):
        self.results = results
        self.summary = summary
        self.timeline_df = timeline_df
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_emotion_name(self, category):
        """Convert category text to clean emotion name"""
        if isinstance(category, str):
            # Remove emoji and clean up
            emotion_map = {
                '⚡ Energised': 'Energised',
                '🔥 Stressed/Tense': 'Stressed/Tense',
                '🌫 Flat/Disengaged': 'Flat/Disengaged',
                '💬 Thoughtful/Constructive': 'Thoughtful/Constructive',
                '🌪 Volatile/Unstable': 'Volatile/Unstable'
            }
            return emotion_map.get(category, category)
        else:
            # Handle numeric categories if any
            emotion_map_num = {
                0: 'Energised',
                1: 'Stressed/Tense', 
                2: 'Flat/Disengaged',
                3: 'Thoughtful/Constructive',
                4: 'Volatile/Unstable'
            }
            return emotion_map_num.get(category, 'Unknown')
    
    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    def generate_txt_report(self):
        """Generate a detailed TXT report"""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("MOODFLO - MEETING EMOTION ANALYSIS REPORT".center(80))
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append(f"Generated: {self.timestamp}")
        report_lines.append(f"File: {self.results.get('filename', 'N/A')}")
        report_lines.append(f"Duration: {self.format_time(self.results['duration'])}")
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("-" * 80)
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        dominant_emotion = self.get_emotion_name(self.summary['dominant_emotion'])
        report_lines.append(f"Dominant Emotion:        {dominant_emotion}")
        report_lines.append(f"Average Energy Level:    {self.summary['avg_energy']:.1f}")
        report_lines.append(f"Silence Percentage:      {self.summary['silence_pct']:.1f}%")
        report_lines.append(f"Participation Rate:      {self.summary['participation']:.1f}%")
        report_lines.append(f"Emotional Volatility:    {self.summary['volatility']:.2f}")
        report_lines.append(f"Psychological Safety:    {self.summary['psych_risk']}")
        report_lines.append("")
        
        # Key Insights
        report_lines.append("-" * 80)
        report_lines.append("AI-POWERED INSIGHTS & RECOMMENDATIONS")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        # Parse suggestions into lines
        suggestions_text = self.results.get('suggestions', 'No insights available.')
        for line in suggestions_text.split('\n'):
            if line.strip():
                report_lines.append(line)
        report_lines.append("")
        
        # Emotion Distribution
        report_lines.append("-" * 80)
        report_lines.append("EMOTION DISTRIBUTION")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        emotion_counts = self.timeline_df['category'].value_counts()
        total_frames = len(self.timeline_df)
        
        for cat_num, count in emotion_counts.items():
            emotion = self.get_emotion_name(cat_num)
            percentage = (count / total_frames) * 100
            bar = "█" * int(percentage / 2)
            report_lines.append(f"{emotion:25} {bar} {percentage:5.1f}%")
        report_lines.append("")
        
        # Timeline Summary (every 30 seconds)
        report_lines.append("-" * 80)
        report_lines.append("EMOTION TIMELINE (30-SECOND INTERVALS)")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append(f"{'Time':>8} | {'Emotion':25} | {'Energy':>6}")
        report_lines.append("-" * 80)
        
        # Sample every 30 seconds
        duration = self.results['duration']
        for t in range(0, int(duration), 30):
            idx = int((t / duration) * len(self.timeline_df))
            if idx < len(self.timeline_df):
                row = self.timeline_df.iloc[idx]
                emotion = self.get_emotion_name(row['category'])
                time_str = self.format_time(t)
                energy = row['energy']
                report_lines.append(f"{time_str:>8} | {emotion:25} | {energy:6.1f}")
        
        report_lines.append("")
        
        # Critical Moments
        report_lines.append("-" * 80)
        report_lines.append("CRITICAL MOMENTS")
        report_lines.append("-" * 80)
        report_lines.append("")
        
        critical_moments = self.results.get('critical_moments', [])
        if critical_moments:
            for moment in critical_moments:
                time_str = self.format_time(moment['time'])
                report_lines.append(f"[{time_str}] {moment['type']}: {moment['description']}")
        else:
            report_lines.append("No critical moments detected.")
        
        report_lines.append("")
        
        # Footer
        report_lines.append("=" * 80)
        report_lines.append("End of Report")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append("This report is confidential and intended for internal use only.")
        report_lines.append("Data processed locally - no information sent to external servers.")
        
        return "\n".join(report_lines)
    
    def generate_pdf_report(self):
        """Generate a professional PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.leading = 14
        
        # Title
        story.append(Paragraph("MOODFLO", title_style))
        story.append(Paragraph("Meeting Emotion Analysis Report", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report Info
        info_data = [
            ["Generated:", self.timestamp],
            ["File:", self.results.get('filename', 'N/A')],
            ["Duration:", self.format_time(self.results['duration'])],
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        
        dominant_emotion = self.get_emotion_name(self.summary['dominant_emotion'])
        
        summary_data = [
            ["Metric", "Value"],
            ["Dominant Emotion", dominant_emotion],
            ["Average Energy Level", f"{self.summary['avg_energy']:.1f}"],
            ["Silence Percentage", f"{self.summary['silence_pct']:.1f}%"],
            ["Participation Rate", f"{self.summary['participation']:.1f}%"],
            ["Emotional Volatility", f"{self.summary['volatility']:.2f}"],
            ["Psychological Safety", self.summary['psych_risk']],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.2*inch))
        
        # AI-Powered Insights & Recommendations
        story.append(Paragraph("AI-Powered Insights & Recommendations", heading_style))
        
        # Parse suggestions text into paragraphs
        suggestions_text = self.results.get('suggestions', 'No insights available.')
        for line in suggestions_text.split('\n'):
            if line.strip():
                story.append(Paragraph(line, normal_style))
                story.append(Spacer(1, 0.05*inch))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(PageBreak())
        
        # Emotion Distribution
        story.append(Paragraph("Emotion Distribution", heading_style))
        
        emotion_counts = self.timeline_df['category'].value_counts()
        total_frames = len(self.timeline_df)
        
        emotion_data = [["Emotion", "Percentage", "Occurrences"]]
        for cat_num, count in emotion_counts.items():
            emotion = self.get_emotion_name(cat_num)
            percentage = (count / total_frames) * 100
            emotion_data.append([emotion, f"{percentage:.1f}%", str(count)])
        
        emotion_table = Table(emotion_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        emotion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(emotion_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Timeline Summary
        story.append(Paragraph("Emotion Timeline (30-second intervals)", heading_style))
        
        timeline_data = [["Time", "Emotion", "Energy"]]
        duration = self.results['duration']
        for t in range(0, int(duration), 30):
            idx = int((t / duration) * len(self.timeline_df))
            if idx < len(self.timeline_df):
                row = self.timeline_df.iloc[idx]
                emotion = self.get_emotion_name(row['category'])
                time_str = self.format_time(t)
                energy = f"{row['energy']:.1f}"
                timeline_data.append([time_str, emotion, energy])
        
        timeline_table = Table(timeline_data, colWidths=[1*inch, 3*inch, 1.5*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(timeline_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Critical Moments
        story.append(Paragraph("Critical Moments", heading_style))
        
        critical_moments = self.results.get('critical_moments', [])
        if critical_moments:
            critical_data = [["Time", "Type", "Description"]]
            for moment in critical_moments:
                time_str = self.format_time(moment['time'])
                critical_data.append([time_str, moment['type'], moment['description']])
            
            critical_table = Table(critical_data, colWidths=[1*inch, 1.5*inch, 3*inch])
            critical_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(critical_table)
        else:
            story.append(Paragraph("No critical moments detected.", normal_style))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Paragraph("<br/><br/>This report is confidential and intended for internal use only.", footer_style))
        story.append(Paragraph("Data processed locally - no information sent to external servers.", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
