import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from modules.analyzer import MeetingAnalyzer
from modules.report_generator import ReportGenerator
import tempfile
import os
import time
from datetime import timedelta, datetime
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Moodflo - Meeting Emotion Analysis",
    page_icon="🎭",
    layout="wide"
)

st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        
        .metric-card {
            background: rgba(30, 30, 46, 0.6);
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.3);
            transition: transform 0.2s;
            backdrop-filter: blur(10px);
            min-height: 140px;
            max-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 1rem;
        }
        
        @media (prefers-color-scheme: light) {
            .metric-card {
                background: rgba(255, 255, 255, 0.8);
                border: 1px solid rgba(102, 126, 234, 0.2);
            }
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.3);
        }
        
        .metric-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.3rem;
            line-height: 1.2;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        .metric-label {
            font-size: 0.75rem;
            color: inherit;
            opacity: 0.7;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 0.2rem;
        }
        
        .privacy-footer {
            text-align: center;
            padding: 1.5rem;
            margin-top: 3rem;
            color: inherit;
            opacity: 0.6;
            font-size: 0.9rem;
            border-top: 1px solid rgba(102, 126, 234, 0.2);
        }
        
        .insights-panel {
            background: rgba(30, 30, 46, 0.6);
            padding: 2rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin-top: 1rem;
            backdrop-filter: blur(10px);
        }
        
        @media (prefers-color-scheme: light) {
            .insights-panel {
                background: rgba(255, 255, 255, 0.8);
            }
        }
        
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            color: #667eea;
        }
        
        .tab-content {
            padding: 1rem 0;
        }
        
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #ff4444;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .video-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎭 Moodflo")
    st.markdown("---")
    
    # OpenAI API Key Input
    st.markdown("#### 🔑 OpenAI API Key")
    api_key_input = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        help="Required for AI-powered insights. Get your key from https://platform.openai.com/api-keys",
        placeholder="sk-..."
    )
    
    if api_key_input:
        st.session_state.openai_api_key = api_key_input
        st.success("✅ API Key saved!")
    elif 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = None
        st.warning("⚠️ Add API key for AI insights")
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Upload Meeting Recording",
        type=['mp4', 'mp3', 'wav', 'avi', 'mov'],
        help="Upload a video or audio file"
    )
    
    st.markdown("---")

st.markdown('<h1 class="main-header">🎭 Moodflo</h1>', unsafe_allow_html=True)

def get_emotion_name(emotion_text):
    emotion_map = {
        '⚡ Energised': 'Energised',
        '🔥 Stressed/Tense': 'Stressed',
        '🌫 Flat/Disengaged': 'Disengaged',
        '💬 Thoughtful/Constructive': 'Thoughtful',
        '🌪 Volatile/Unstable': 'Volatile'
    }
    return emotion_map.get(emotion_text, emotion_text.split()[-1] if ' ' in emotion_text else emotion_text)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

def create_video_player(video_path):
    """Create custom HTML5 video player with real-time playback tracking"""
    with open(video_path, 'rb') as video_file:
        video_bytes = video_file.read()
    video_base64 = base64.b64encode(video_bytes).decode()
    
    ext = os.path.splitext(video_path)[1].lower()
    mime_types = {
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav'
    }
    mime_type = mime_types.get(ext, 'video/mp4')
    is_audio = ext in ['.mp3', '.wav']
    
    player_html = f"""
    <div style="width: 100%; max-width: 800px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
        {'<audio' if is_audio else '<video'} 
            id="meetingPlayer" 
            controls 
            style="width: 100%; border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);"
            onloadedmetadata="initPlayer()"
            ontimeupdate="updatePlaybackTime()"
            onplay="updatePlaybackTime()"
            onpause="updatePlaybackTime()"
            onseeked="updatePlaybackTime()">
            <source src="data:{mime_type};base64,{video_base64}" type="{mime_type}">
            Your browser does not support the video/audio element.
        {'</audio>' if is_audio else '</video>'}
        
        <div style="margin-top: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: #667eea;">
                <span id="currentTime">0:00</span>
                <span id="duration">0:00</span>
            </div>
            
            <!-- Custom Progress Bar/Slider -->
            <div style="position: relative; width: 100%; height: 8px; background: rgba(102, 126, 234, 0.2); border-radius: 4px; cursor: pointer;" id="progressBar" onclick="seekVideo(event)">
                <div id="progressFill" style="height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 4px; width: 0%; transition: width 0.1s;"></div>
                <div id="progressHandle" style="position: absolute; top: 50%; right: 0; transform: translate(50%, -50%); width: 16px; height: 16px; background: white; border: 2px solid #667eea; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.3); cursor: grab;"></div>
            </div>
        </div>
    </div>
    
    <script>
        const player = document.getElementById('meetingPlayer');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const progressHandle = document.getElementById('progressHandle');
        let lastSentTime = -1;
        let isDragging = false;
        
        function initPlayer() {{
            const duration = player.duration;
            document.getElementById('duration').textContent = formatTime(duration);
            console.log('Player initialized, duration:', duration);
        }}
        
        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return mins + ':' + (secs < 10 ? '0' : '') + secs;
        }}
        
        function updateProgressBar() {{
            if (!isDragging && player.duration) {{
                const percent = (player.currentTime / player.duration) * 100;
                progressFill.style.width = percent + '%';
            }}
        }}
        
        function seekVideo(event) {{
            if (player.duration) {{
                const rect = progressBar.getBoundingClientRect();
                const percent = (event.clientX - rect.left) / rect.width;
                const newTime = percent * player.duration;
                player.currentTime = newTime;
                updatePlaybackTime();
            }}
        }}
        
        function updatePlaybackTime() {{
            const currentTime = player.currentTime;
            document.getElementById('currentTime').textContent = formatTime(currentTime);
            updateProgressBar();
            
            // Send to Streamlit with throttling
            if (Math.abs(currentTime - lastSentTime) > 0.5 || player.paused) {{
                console.log('Sending time to Streamlit:', currentTime);
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: currentTime
                }}, '*');
                lastSentTime = currentTime;
            }}
        }}
        
        // Update every 200ms during playback for smooth progress bar
        setInterval(function() {{
            if (!player.paused && !player.ended) {{
                updatePlaybackTime();
            }}
        }}, 200);
        
        // Initialize when player is ready
        player.addEventListener('loadeddata', function() {{
            console.log('Player ready to play');
            updatePlaybackTime();
        }});
        
        // Drag functionality for progress handle
        progressHandle.addEventListener('mousedown', function(e) {{
            isDragging = true;
            e.preventDefault();
        }});
        
        document.addEventListener('mousemove', function(e) {{
            if (isDragging && player.duration) {{
                const rect = progressBar.getBoundingClientRect();
                let percent = (e.clientX - rect.left) / rect.width;
                percent = Math.max(0, Math.min(1, percent));
                progressFill.style.width = (percent * 100) + '%';
            }}
        }});
        
        document.addEventListener('mouseup', function(e) {{
            if (isDragging && player.duration) {{
                const rect = progressBar.getBoundingClientRect();
                let percent = (e.clientX - rect.left) / rect.width;
                percent = Math.max(0, Math.min(1, percent));
                player.currentTime = percent * player.duration;
                updatePlaybackTime();
            }}
            isDragging = false;
        }});
    </script>
    """
    
    return player_html

if uploaded_file is not None:
    
    if 'analysis_complete' not in st.session_state or st.session_state.get('current_file') != uploaded_file.name:
        st.session_state.analysis_complete = False
        st.session_state.current_file = uploaded_file.name
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        temp_file.write(uploaded_file.read())
        temp_file.close()
        st.session_state.temp_file_path = temp_file.name
        
        st.markdown("### 🔄 Processing Analysis...")
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(value, message):
                progress_bar.progress(value)
                status_text.text(message)
            
            start_time = time.time()
            # Pass API key from sidebar to analyzer
            api_key = st.session_state.get('openai_api_key', None)
            analyzer = MeetingAnalyzer(openai_api_key=api_key)
            results = analyzer.analyze(st.session_state.temp_file_path, progress_callback=update_progress)
            processing_time = time.time() - start_time
            
            progress_bar.progress(100)
            status_text.success(f"✅ Analysis complete in {processing_time:.1f}s!")
        
        st.session_state.results = results
        st.session_state.analysis_complete = True
        st.session_state.processing_time = processing_time
        time.sleep(1)
        st.rerun()
    
    if st.session_state.analysis_complete:
        results = st.session_state.results
        summary = results['summary']
        timeline_df = results['timeline']
        
        tab1, tab2 = st.tabs([
            "📊 Overall Analysis", 
            "🔴 Live Dashboard"
        ])
        
        with tab1:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
            
            st.markdown("## 📈 Meeting Overview")
            
            kpi_row1 = st.columns(3)
            
            with kpi_row1[0]:
                emotion_display = get_emotion_name(summary['dominant_emotion'])
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{emotion_display}</div>
                        <div class="metric-label">Dominant Emotion</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with kpi_row1[1]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{summary['avg_energy']:.0f}</div>
                        <div class="metric-label">Avg Energy</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with kpi_row1[2]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{summary['silence_pct']:.0f}%</div>
                        <div class="metric-label">Silence</div>
                    </div>
                """, unsafe_allow_html=True)
            
            kpi_row2 = st.columns(3)
            
            with kpi_row2[0]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{summary['participation']:.0f}%</div>
                        <div class="metric-label">Participation</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with kpi_row2[1]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{summary['volatility']:.1f}</div>
                        <div class="metric-label">Volatility</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with kpi_row2[2]:
                risk_color = {'Low': '#00d4aa', 'Medium': '#ffa500', 'High': '#ff4444'}[summary['psych_risk']]
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: {risk_color};">{summary['psych_risk']}</div>
                        <div class="metric-label">Psych Safety</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📊 Complete Emotion Timeline")
                
                fig = go.Figure()
                
                colors = {'⚡ Energised': '#00d4aa', '🔥 Stressed/Tense': '#ff4444', 
                         '🌫 Flat/Disengaged': '#888888', '💬 Thoughtful/Constructive': '#667eea',
                         '🌪 Volatile/Unstable': '#ffa500'}
                
                timeline_df['time_minutes'] = timeline_df['time'] / 60
                
                # Create color array for each point
                point_colors = [colors.get(cat, '#667eea') for cat in timeline_df['category']]
                
                # Add single trace with gradient colors
                fig.add_trace(go.Scatter(
                    x=timeline_df['time_minutes'],
                    y=timeline_df['energy'],
                    mode='lines+markers',
                    line=dict(color='rgba(255,255,255,0.3)', width=1),
                    marker=dict(
                        size=8,
                        color=point_colors,
                        line=dict(width=0)
                    ),
                    hovertemplate='<b>%{text}</b><br>Energy: %{y:.1f}<br>Time: %{x:.2f} min<extra></extra>',
                    text=timeline_df['category'],
                    showlegend=False
                ))
                
                # Add legend entries manually
                for category, color in colors.items():
                    if category in timeline_df['category'].values:
                        fig.add_trace(go.Scatter(
                            x=[None], y=[None],
                            mode='markers',
                            marker=dict(size=10, color=color),
                            name=category,
                            showlegend=True
                        ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=400,
                    hovermode='closest',
                    xaxis_title='Time (minutes)',
                    yaxis_title='Energy Level',
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 🎯 Emotion Distribution")
                
                dist_df = pd.DataFrame({
                    'Emotion': list(summary['distribution'].keys()),
                    'Percentage': list(summary['distribution'].values())
                })
                
                fig = go.Figure(data=[go.Pie(
                    labels=dist_df['Emotion'],
                    values=dist_df['Percentage'],
                    hole=0.5,
                    marker=dict(colors=['#00d4aa', '#667eea', '#ff4444', '#ffa500', '#888888'])
                )])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔬 Team Clustering")
                
                cluster_data = results['clusters']
                
                # Map cluster numbers to meaningful names
                cluster_names = {
                    0: 'High Energy Group',
                    1: 'Stressed/Tense Group',
                    2: 'Calm/Neutral Group',
                    3: 'Low Energy Group'
                }
                
                cluster_df = pd.DataFrame({
                    'x': [coord[0] for coord in cluster_data['coordinates']],
                    'y': [coord[1] for coord in cluster_data['coordinates']],
                    'cluster': cluster_data['labels'],
                    'cluster_name': [cluster_names.get(label, f'Group {label}') for label in cluster_data['labels']]
                })
                
                fig = px.scatter(
                    cluster_df, x='x', y='y', color='cluster',
                    color_continuous_scale='Viridis',
                    labels={'x': 'Dimension 1', 'y': 'Dimension 2'},
                    hover_data={'cluster_name': True, 'cluster': False, 'x': False, 'y': False}
                )
                
                fig.update_traces(
                    hovertemplate='<b>%{customdata[0]}</b><extra></extra>'
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 📊 Metrics Breakdown")
                
                metrics_df = pd.DataFrame({
                    'Metric': ['Energy', 'Participation', 'Silence', 'Volatility'],
                    'Value': [
                        summary['avg_energy'],
                        summary['participation'],
                        summary['silence_pct'],
                        summary['volatility'] * 10
                    ]
                })
                
                fig = go.Figure(data=[go.Bar(
                    x=metrics_df['Metric'],
                    y=metrics_df['Value'],
                    marker_color=['#667eea', '#00d4aa', '#ff4444', '#ffa500']
                )])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col3:
                st.markdown("### 📈 Energy Trajectory")
                
                energy_smooth = pd.Series(timeline_df['energy']).rolling(window=5, center=True).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timeline_df['time_minutes'],
                    y=energy_smooth,
                    fill='tozeroy',
                    line=dict(color='#667eea', width=2),
                    name='Energy'
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=350,
                    showlegend=False,
                    xaxis_title='Time (min)',
                    yaxis_title='Energy'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎵 Speaking Pattern Analysis")
                
                bin_size = max(1, len(timeline_df) // 20)
                timeline_df['time_bin'] = timeline_df.index // bin_size
                pattern = timeline_df.groupby('time_bin')['energy'].agg(['mean', 'std']).reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=pattern.index,
                    y=pattern['mean'],
                    mode='lines+markers',
                    name='Avg Energy',
                    line=dict(color='#667eea', width=2),
                    marker=dict(size=6)
                ))
                fig.add_trace(go.Scatter(
                    x=pattern.index,
                    y=pattern['std'],
                    mode='lines',
                    name='Variability',
                    line=dict(color='#ffa500', width=2, dash='dash')
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=350,
                    xaxis_title='Meeting Segment',
                    yaxis_title='Value'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 📉 Emotion Transitions")
                
                category_numeric = timeline_df['category'].map({
                    '⚡ Energised': 4,
                    '💬 Thoughtful/Constructive': 3,
                    '🌫 Flat/Disengaged': 2,
                    '🔥 Stressed/Tense': 1,
                    '🌪 Volatile/Unstable': 0
                }).fillna(2)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timeline_df['time_minutes'],
                    y=category_numeric,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color='#00d4aa', width=2),
                    hovertemplate='%{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=350,
                    xaxis_title='Time (min)',
                    yaxis=dict(
                        tickmode='array',
                        tickvals=[0, 1, 2, 3, 4],
                        ticktext=['Volatile', 'Stressed', 'Disengaged', 'Thoughtful', 'Energised']
                    )
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.markdown("---")
            st.markdown("## 💡 AI-Powered Insights")
            
            st.markdown(f'<div class="insights-panel">{results["suggestions"]}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("## 📥 Export Reports")
            
            export_col1, export_col2 = st.columns([1.5, 1.5])
            
            report_gen = ReportGenerator(results, summary, timeline_df)
            txt_report = report_gen.generate_txt_report()
            pdf_buffer = report_gen.generate_pdf_report()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            with export_col1:
                st.download_button(
                    label="📄 Download TXT Report",
                    data=txt_report,
                    file_name=f"moodflo_report_{timestamp}.txt",
                    mime="text/plain",
                    width='stretch',
                    help="Download comprehensive text report with all analysis"
                )
            
            with export_col2:
                st.download_button(
                    label="📑 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"moodflo_report_{timestamp}.pdf",
                    mime="application/pdf",
                    width='stretch',
                    help="Download professional PDF report with formatted tables"
                )
            
            st.markdown("---")
            
            info_cols = st.columns(2)
            with info_cols[0]:
                st.metric("Meeting Duration", f"{int(results['duration'] // 60)}m {int(results['duration'] % 60)}s")
            with info_cols[1]:
                st.metric("Processing Time", f"{st.session_state.processing_time:.1f}s")
            
            st.markdown('<div class="privacy-footer">🔒 Privacy Protected: Only voice tone analyzed. No content recorded or stored.</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="tab-content">', unsafe_allow_html=True)
 
            if 'playback_time' not in st.session_state:
                st.session_state.playback_time = 0
            
            # Add auto-refresh for live updates
            if 'auto_refresh' not in st.session_state:
                st.session_state.auto_refresh = False
            
            col_video, col_live = st.columns([1, 1])
            
            with col_video:
                st.markdown("### 📹 Meeting Recording")
                
                # Simple video player without custom controls
                ext = os.path.splitext(st.session_state.temp_file_path)[1].lower()
                is_audio = ext in ['.mp3', '.wav']
                
                if is_audio:
                    st.audio(st.session_state.temp_file_path)
                else:
                    st.video(st.session_state.temp_file_path)
                
                st.caption("📹 Watch the video and use the slider to analyze any moment")
            
                # Manual time slider in minutes
                max_minutes = results['duration'] / 60
                
                playback_minutes = st.slider(
                    "Seek to time (minutes)",
                    min_value=0.0,
                    max_value=float(max_minutes),
                    value=float(st.session_state.playback_time / 60),
                    step=0.1,
                    format="%.1f min",
                    help="Drag to analyze any moment in the meeting"
                )
                
                # Convert back to seconds
                playback_time = playback_minutes * 60
                st.session_state.playback_time = playback_time

                
                current_idx = int((playback_time / results['duration']) * len(timeline_df))
                current_idx = min(max(current_idx, 0), len(timeline_df) - 1)
                
                current_data = timeline_df.iloc[:current_idx+1].copy() if current_idx > 0 else timeline_df.iloc[:1].copy()
                current_emotion = timeline_df.iloc[current_idx]['category']
                current_energy = timeline_df.iloc[current_idx]['energy']
            
            with col_live:

                st.markdown("## 🔑 Key Performance Indicators")
                st.markdown("---")
                
                live_kpi_row1 = st.columns(3)
                
                with live_kpi_row1[0]:
                    emotion_display = get_emotion_name(current_emotion)
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{emotion_display}</div>
                            <div class="metric-label">Current Emotion</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with live_kpi_row1[1]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{current_energy:.0f}</div>
                            <div class="metric-label">Current Energy</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with live_kpi_row1[2]:
                    current_silence = (current_data['energy'] < 20).sum() / len(current_data) * 100 if len(current_data) > 0 else 0
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{current_silence:.0f}%</div>
                            <div class="metric-label">Silence So Far</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                live_kpi_row2 = st.columns(3)
                
                with live_kpi_row2[0]:
                    avg_energy = current_data['energy'].mean() if len(current_data) > 0 else 0
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{avg_energy:.0f}</div>
                            <div class="metric-label">Average Energy</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with live_kpi_row2[1]:
                    emotion_changes = (current_data['category'].shift() != current_data['category']).sum() if len(current_data) > 1 else 0
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{emotion_changes}</div>
                            <div class="metric-label">Emotion Shifts</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with live_kpi_row2[2]:
                    elapsed_time = format_time(playback_time)
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{elapsed_time}</div>
                            <div class="metric-label">Elapsed Time</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📈 Live Emotion Timeline")
                
                fig = go.Figure()
                
                colors_map = {'⚡ Energised': '#00d4aa', '🔥 Stressed/Tense': '#ff4444', 
                             '🌫 Flat/Disengaged': '#888888', '💬 Thoughtful/Constructive': '#667eea',
                             '🌪 Volatile/Unstable': '#ffa500'}
                
                current_data['time_minutes'] = current_data['time'] / 60
                
                # Create color array for each point
                point_colors = [colors_map.get(cat, '#667eea') for cat in current_data['category']]
                
                # Add single trace with gradient colors
                fig.add_trace(go.Scatter(
                    x=current_data['time_minutes'],
                    y=current_data['energy'],
                    mode='lines+markers',
                    line=dict(color='rgba(255,255,255,0.3)', width=1),
                    marker=dict(
                        size=8,
                        color=point_colors,
                        line=dict(width=0)
                    ),
                    hovertemplate='<b>%{text}</b><br>Energy: %{y:.1f}<br>Time: %{x:.2f} min<extra></extra>',
                    text=current_data['category'],
                    showlegend=False
                ))
                
                # Add legend entries manually
                for category, color in colors_map.items():
                    if category in current_data['category'].values:
                        fig.add_trace(go.Scatter(
                            x=[None], y=[None],
                            mode='markers',
                            marker=dict(size=10, color=color),
                            name=category,
                            showlegend=True
                        ))
                
                fig.add_vline(x=playback_time/60, line_dash="dash", line_color="white", line_width=2, annotation_text="Now")
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=400,
                    xaxis_title='Time (minutes)',
                    yaxis_title='Energy Level',
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 🎯 Live Distribution")
                
                current_dist = current_data['category'].value_counts(normalize=True) * 100
                
                fig = go.Figure(data=[go.Pie(
                    labels=current_dist.index,
                    values=current_dist.values,
                    hole=0.5,
                    marker=dict(colors=['#00d4aa', '#667eea', '#ff4444', '#ffa500', '#888888'])
                )])
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=400
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### ⚡ Energy Gauge")
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=current_energy,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 30], 'color': "#888888"},
                            {'range': [30, 70], 'color': "#00d4aa"},
                            {'range': [70, 100], 'color': "#ffa500"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#fafafa'},
                    height=300
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 📊 Running Avg Energy")
                
                running_avg = current_data['energy'].expanding().mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=current_data['time_minutes'],
                    y=running_avg,
                    fill='tozeroy',
                    line=dict(color='#667eea', width=2)
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=300,
                    xaxis_title='Time (min)',
                    yaxis_title='Avg Energy'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            with col3:
                st.markdown("### 🌊 Emotion Volatility")
                
                category_num = current_data['category'].map({
                    '⚡ Energised': 4, '💬 Thoughtful/Constructive': 3,
                    '🌫 Flat/Disengaged': 2, '🔥 Stressed/Tense': 1,
                    '🌪 Volatile/Unstable': 0
                }).fillna(2)
                
                volatility = category_num.diff().abs().rolling(window=5).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=current_data['time_minutes'],
                    y=volatility,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color='#ffa500', width=2)
                ))
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(),
                    height=300,
                    xaxis_title='Time (min)',
                    yaxis_title='Volatility'
                )
                
                st.plotly_chart(fig, width='stretch')
            
            st.markdown('<div class="privacy-footer">🔒 Privacy Protected: Only voice tone analyzed. No content recorded or stored.</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 Upload a meeting recording to begin analysis")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 About")
        st.markdown("Real-time emotion analysis for meetings.")
    
    with col2:
        st.markdown("### ֎ AI-Powered")
        st.markdown("GPT-4 generates actionable meeting insights.")
    
    st.markdown('<div class="privacy-footer">🔒 Privacy Protected: Only voice tone analyzed. No content recorded or stored.</div>', unsafe_allow_html=True)
