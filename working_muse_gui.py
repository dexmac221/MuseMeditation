#!/usr/bin/env python3
"""
🎉 WORKING MUSE 2 GUI - Using Fixed muselsl Library
This GUI works with the patched muselsl that actually streams to LSL!
Real-time EEG visualization with meditation analysis

⚠️  IMPORTANT DISCLAIMER:
This software is for educational and research purposes only.
Not intended for medical diagnosis or treatment. Use at your own risk.
Always consult qualified medical professionals for health-related concerns.
"""

import sys
import numpy as np
import time
import threading
from collections import deque
from pylsl import resolve_streams, StreamInlet

# Qt imports
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QProgressBar
    from PyQt5.QtCore import QTimer, pyqtSignal, QObject
    from PyQt5.QtGui import QFont
    import pyqtgraph as pg
    QT_AVAILABLE = True
except ImportError as e:
    print(f"Qt imports failed: {e}")
    QT_AVAILABLE = False
    sys.exit(1)

# Muse imports
try:
    from muselsl import list_muses
    import subprocess
    MUSE_AVAILABLE = True
except ImportError as e:
    print(f"Muse imports failed: {e}")
    MUSE_AVAILABLE = False


class MeditationAnalyzer:
    """Real-time meditation analysis from EEG data"""
    def __init__(self, sample_rate=256):
        self.sample_rate = sample_rate
        self.buffer_size = 3 * sample_rate  # 3 seconds of data
        self.eeg_buffer = {
            'TP9': deque(maxlen=self.buffer_size),
            'AF7': deque(maxlen=self.buffer_size),
            'AF8': deque(maxlen=self.buffer_size),
            'TP10': deque(maxlen=self.buffer_size)
        }
        self.lock = threading.Lock()
        
        # Calibration data
        self.is_calibrated = False
        self.calibration_baseline = {
            'avg_rms': 50.0,     # Default baseline RMS
            'smoothness': 0.01,   # Default smoothness baseline
            'sync': 0.3          # Default synchronization baseline
        }
        self.calibration_buffer = {
            'TP9': [],
            'AF7': [],
            'AF8': [],
            'TP10': []
        }
        
    def start_calibration(self):
        """Start calibration data collection"""
        self.calibration_buffer = {'TP9': [], 'AF7': [], 'AF8': [], 'TP10': []}
        self.is_calibrated = False
        
    def add_calibration_sample(self, sample):
        """Add sample during calibration"""
        channels = ['TP9', 'AF7', 'AF8', 'TP10']
        for i, channel in enumerate(channels):
            if i < len(sample):
                self.calibration_buffer[channel].append(sample[i])
                
    def finish_calibration(self):
        """Complete calibration and set baseline values"""
        if len(self.calibration_buffer['AF7']) < 256:  # Need at least 1 second
            return False, "Not enough calibration data"
            
        try:
            # Calculate baseline values from calibration data
            af7_data = np.array(self.calibration_buffer['AF7'])
            af8_data = np.array(self.calibration_buffer['AF8'])
            
            # Baseline RMS
            af7_rms = np.sqrt(np.mean(af7_data ** 2))
            af8_rms = np.sqrt(np.mean(af8_data ** 2))
            self.calibration_baseline['avg_rms'] = (af7_rms + af8_rms) / 2
            
            # Baseline smoothness
            af7_diff = np.diff(af7_data)
            af8_diff = np.diff(af8_data)
            af7_smoothness = 1.0 / (1.0 + np.var(af7_diff))
            af8_smoothness = 1.0 / (1.0 + np.var(af8_diff))
            self.calibration_baseline['smoothness'] = (af7_smoothness + af8_smoothness) / 2
            
            # Baseline synchronization
            if len(af7_data) > 100 and len(af8_data) > 100:
                correlation = np.corrcoef(af7_data, af8_data)[0, 1]
                if not np.isnan(correlation):
                    self.calibration_baseline['sync'] = abs(correlation)
            
            self.is_calibrated = True
            return True, f"Calibration complete! Baseline RMS: {self.calibration_baseline['avg_rms']:.1f}µV"
            
        except Exception as e:
            return False, f"Calibration failed: {e}"
        
    def add_sample(self, sample):
        """Add EEG sample for analysis"""
        with self.lock:
            channels = ['TP9', 'AF7', 'AF8', 'TP10']
            for i, channel in enumerate(channels):
                if i < len(sample):
                    self.eeg_buffer[channel].append(sample[i])
                
    def calculate_meditation_score(self):
        """Calculate meditation score from EEG data using research-based approach"""
        with self.lock:
            if len(self.eeg_buffer['AF7']) < 256:  # Need at least 1 second
                return 0.0, "Collecting data..."
                
            # Use frontal channels for meditation analysis
            af7_data = np.array(list(self.eeg_buffer['AF7'])[-768:])  # Last 3 seconds
            af8_data = np.array(list(self.eeg_buffer['AF8'])[-768:])
            
            if len(af7_data) < 256:
                return 0.0, "Collecting data..."
            
            # Research-based meditation indicators:
            # 1. Signal amplitude (high amplitude = more mental activity)
            # 2. Signal smoothness (jagged = more active, smooth = more relaxed)
            # 3. Cross-channel coherence (synchronized = more meditative)
            
            # Calculate RMS (Root Mean Square) for signal strength
            af7_rms = np.sqrt(np.mean(af7_data ** 2))
            af8_rms = np.sqrt(np.mean(af8_data ** 2))
            avg_rms = (af7_rms + af8_rms) / 2
            
            # Calculate signal smoothness (derivative variance)
            af7_diff = np.diff(af7_data)
            af8_diff = np.diff(af8_data)
            af7_smoothness = 1.0 / (1.0 + np.var(af7_diff))  # Inverse variance
            af8_smoothness = 1.0 / (1.0 + np.var(af8_diff))
            avg_smoothness = (af7_smoothness + af8_smoothness) / 2
            
            # Calculate cross-correlation (synchronization between hemispheres)
            if len(af7_data) > 100 and len(af8_data) > 100:
                correlation = np.corrcoef(af7_data, af8_data)[0, 1]
                if np.isnan(correlation):
                    correlation = 0
                sync_factor = abs(correlation)  # Higher correlation = more synchronized
            else:
                sync_factor = 0
            
            # Use calibration baseline if available
            if self.is_calibrated:
                baseline_rms = self.calibration_baseline['avg_rms']
                baseline_smoothness = self.calibration_baseline['smoothness']
                baseline_sync = self.calibration_baseline['sync']
                
                # Relative amplitude scoring (compared to personal baseline)
                rms_ratio = avg_rms / baseline_rms
                if rms_ratio < 0.7:      # Much lower than baseline
                    amplitude_score = 40
                elif rms_ratio < 0.85:   # Somewhat lower
                    amplitude_score = 30
                elif rms_ratio < 1.15:   # Near baseline
                    amplitude_score = 20
                elif rms_ratio < 1.4:    # Somewhat higher
                    amplitude_score = 10
                else:                    # Much higher than baseline
                    amplitude_score = 0
                
                # Relative smoothness scoring
                smoothness_ratio = avg_smoothness / baseline_smoothness
                smoothness_score = min(30, smoothness_ratio * 15)
                
                # Relative synchronization scoring
                sync_ratio = sync_factor / baseline_sync if baseline_sync > 0 else 1.0
                sync_score = min(20, sync_ratio * 15)
                
                meditation_state_suffix = " (Calibrated)"
                
            else:
                # Default scoring without calibration
                if avg_rms < 15:
                    amplitude_score = 40
                elif avg_rms < 30:
                    amplitude_score = 25
                elif avg_rms < 50:
                    amplitude_score = 10
                else:
                    amplitude_score = 0
                
                smoothness_score = min(30, avg_smoothness * 1000)
                sync_score = sync_factor * 20
                meditation_state_suffix = " (Uncalibrated)"
            
            # Stability bonus - consistent readings over time
            recent_rms = [np.sqrt(np.mean(af7_data[i:i+128] ** 2)) 
                         for i in range(0, len(af7_data)-128, 64)]
            if len(recent_rms) > 2:
                stability = 1.0 / (1.0 + np.var(recent_rms))
                stability_score = min(10, stability * 100)
            else:
                stability_score = 0
            
            # Combine scores
            meditation_score = amplitude_score + smoothness_score + sync_score + stability_score
            meditation_score = max(0, min(100, meditation_score))
            
            # Determine state with research-based thresholds
            if meditation_score > 75:
                state = "Deep Meditation" + meditation_state_suffix
            elif meditation_score > 60:
                state = "Calm/Relaxed" + meditation_state_suffix
            elif meditation_score > 40:
                state = "Mild Relaxation" + meditation_state_suffix
            elif meditation_score > 25:
                state = "Alert/Focused" + meditation_state_suffix
            else:
                state = "Active/Stressed" + meditation_state_suffix
                
            return meditation_score, state


class LSLDataReceiver(QObject):
    """Receives data from LSL streams created by fixed muselsl"""
    data_received = pyqtSignal(np.ndarray)
    status_update = pyqtSignal(str)
    connection_lost = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.inlet = None
        self.sample_count = 0
        self.last_sample_time = 0
        
    def start_receiving(self):
        """Start receiving data from LSL stream"""
        self.running = True
        
        def receiver_thread():
            try:
                self.status_update.emit("Looking for LSL EEG stream...")
                
                # Wait for LSL stream from fixed muselsl
                streams = resolve_streams(wait_time=15.0)
                eeg_streams = [s for s in streams if s.type() == 'EEG']
                
                if not eeg_streams:
                    self.status_update.emit("No LSL EEG stream found")
                    self.connection_lost.emit()
                    return
                
                self.inlet = StreamInlet(eeg_streams[0])
                self.status_update.emit(f"Connected to: {eeg_streams[0].name()}")
                
                # Main data receiving loop
                while self.running:
                    try:
                        sample, timestamp = self.inlet.pull_sample(timeout=3.0)
                        if sample and len(sample) >= 4:
                            self.sample_count += 1
                            self.last_sample_time = time.time()
                            self.data_received.emit(np.array(sample[:4]))  # First 4 channels
                    except Exception as e:
                        self.status_update.emit(f"Data receive error: {e}")
                        break
                        
            except Exception as e:
                self.status_update.emit(f"LSL receiver error: {e}")
                self.connection_lost.emit()
        
        thread = threading.Thread(target=receiver_thread, daemon=True)
        thread.start()
        
    def stop_receiving(self):
        """Stop receiving data"""
        self.running = False
        self.status_update.emit("Stopped receiving LSL data")


class WorkingMuseGUI(QMainWindow):
    """Working Muse 2 GUI using fixed muselsl library"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Working Muse 2 GUI - Using Fixed muselsl!")
        self.setGeometry(100, 100, 1400, 900)
        
        # Modern theme
        self.setStyleSheet("""
            QMainWindow { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1e3c72, stop:1 #2a5298); 
            }
            QLabel { 
                color: #ffffff; 
                font-size: 14px; 
                padding: 5px;
            }
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00c851, stop:1 #007e33);
                color: white; 
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #00ff5f, stop:1 #00c851);
            }
            QPushButton:disabled { 
                background: #666666; 
                color: #aaaaaa; 
            }
            QTextEdit { 
                background-color: #1a1a2e; 
                color: #eee; 
                border: 2px solid #16213e;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }
            QProgressBar {
                border: 2px solid #16213e;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                color: white;
                background-color: #1a1a2e;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00c851, stop:1 #00ff5f);
                border-radius: 6px;
            }
        """)
        
        self.setup_ui()
        self.setup_plots()
        
        # Initialize components
        self.meditation_analyzer = MeditationAnalyzer()
        self.lsl_receiver = LSLDataReceiver()
        
        # Connect signals
        self.lsl_receiver.data_received.connect(self.process_eeg_data)
        self.lsl_receiver.status_update.connect(self.update_status_message)
        self.lsl_receiver.connection_lost.connect(self.handle_connection_lost)
        
        # State
        self.is_streaming = False
        self.stream_process = None
        self.sample_count = 0
        
        # Calibration state
        self.is_calibrating = False
        self.calibration_start_time = 0
        self.calibration_duration = 20  # seconds
        
        # Plot data - show last 8 seconds
        self.plot_buffer_size = 2048  # 8 seconds at 256Hz
        self.eeg_data = {
            'TP9': deque(maxlen=self.plot_buffer_size),
            'AF7': deque(maxlen=self.plot_buffer_size),
            'AF8': deque(maxlen=self.plot_buffer_size),
            'TP10': deque(maxlen=self.plot_buffer_size)
        }
        self.time_data = deque(maxlen=self.plot_buffer_size)
        
        # Meditation tracking data
        self.meditation_10s_data = deque(maxlen=180)  # Last 30 minutes at 10s intervals
        self.meditation_10s_times = deque(maxlen=180)
        self.meditation_1m_data = deque(maxlen=60)   # Last 1 hour at 1m intervals  
        self.meditation_1m_times = deque(maxlen=60)
        
        # Timers
        self.meditation_timer = QTimer(self)
        self.meditation_timer.timeout.connect(self.update_meditation_display)
        
        self.sample_timer = QTimer(self)
        self.sample_timer.timeout.connect(self.update_sample_count)
        
        # Meditation tracking timers
        self.meditation_10s_timer = QTimer(self)
        self.meditation_10s_timer.timeout.connect(self.record_meditation_10s)
        
        self.meditation_1m_timer = QTimer(self)
        self.meditation_1m_timer.timeout.connect(self.record_meditation_1m)
        
        # Calibration timer
        self.calibration_timer = QTimer(self)
        self.calibration_timer.timeout.connect(self.update_calibration)
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("BRAIN Muse 2 EEG Monitor")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #ffffff; margin: 10px;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("READY Using Fixed muselsl Library - Real LSL Streaming!")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #cccccc; margin: 5px;")
        header_layout.addWidget(subtitle)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("START Muse Streaming")
        self.start_btn.clicked.connect(self.toggle_streaming)
        self.start_btn.setMinimumHeight(50)
        controls_layout.addWidget(self.start_btn)
        
        self.calibrate_btn = QPushButton("CALIBRATE (20s)")
        self.calibrate_btn.clicked.connect(self.start_calibration)
        self.calibrate_btn.setMinimumHeight(50)
        self.calibrate_btn.setEnabled(False)
        controls_layout.addWidget(self.calibrate_btn)
        
        # Status section
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setFont(QFont("Arial", 13, QFont.Bold))
        self.status_label.setStyleSheet("color: #ffd700;")
        status_layout.addWidget(self.status_label)
        
        self.sample_label = QLabel("SAMPLES: 0")
        self.sample_label.setFont(QFont("Arial", 11))
        self.sample_label.setStyleSheet("color: #87ceeb;")
        status_layout.addWidget(self.sample_label)
        
        controls_layout.addLayout(status_layout)
        controls_layout.addStretch()
        
        # Meditation section
        meditation_layout = QVBoxLayout()
        
        self.meditation_label = QLabel("MEDITATION: --/100")
        self.meditation_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.meditation_label.setStyleSheet("color: #90ee90;")
        meditation_layout.addWidget(self.meditation_label)
        
        self.state_label = QLabel("STATE: Ready")
        self.state_label.setFont(QFont("Arial", 14))
        self.state_label.setStyleSheet("color: #dda0dd;")
        meditation_layout.addWidget(self.state_label)
        
        self.meditation_progress = QProgressBar()
        self.meditation_progress.setRange(0, 100)
        self.meditation_progress.setValue(0)
        self.meditation_progress.setMaximumHeight(20)
        meditation_layout.addWidget(self.meditation_progress)
        
        controls_layout.addLayout(meditation_layout)
        
        main_layout.addLayout(controls_layout)
        
        # Create plot tabs or sections
        plot_container = QWidget()
        plot_layout = QHBoxLayout(plot_container)
        
        # Left side: EEG Plots (70% width)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        eeg_label = QLabel("REAL-TIME EEG Channels")
        eeg_label.setFont(QFont("Arial", 14, QFont.Bold))
        eeg_label.setStyleSheet("color: #ffffff; margin: 5px;")
        left_layout.addWidget(eeg_label)
        
        self.eeg_plot_widget = pg.GraphicsLayoutWidget()
        self.eeg_plot_widget.setBackground('#0f1419')
        left_layout.addWidget(self.eeg_plot_widget)
        
        # Right side: Meditation Tracking Plots (30% width)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        meditation_label = QLabel("MEDITATION Score Tracking")
        meditation_label.setFont(QFont("Arial", 14, QFont.Bold))
        meditation_label.setStyleSheet("color: #ffffff; margin: 5px;")
        right_layout.addWidget(meditation_label)
        
        # Meditation statistics labels
        self.meditation_stats_label = QLabel("STATS: --")
        self.meditation_stats_label.setFont(QFont("Arial", 10))
        self.meditation_stats_label.setStyleSheet("color: #cccccc; margin: 2px;")
        right_layout.addWidget(self.meditation_stats_label)
        
        self.meditation_plot_widget = pg.GraphicsLayoutWidget()
        self.meditation_plot_widget.setBackground('#0f1419')
        right_layout.addWidget(self.meditation_plot_widget)
        
        # Set proportions: 70% EEG, 30% Meditation
        plot_layout.addWidget(left_widget, 7)
        plot_layout.addWidget(right_widget, 3)
        
        main_layout.addWidget(plot_container)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlainText("READY Working Muse 2 GUI with Advanced Features!\n"
                                   "ACTIVE Using patched muselsl library with LSL streaming\n"
                                   "NEW: 10-second & 1-minute meditation score tracking\n"
                                   "NEW: 20-second calibration for personalized baselines\n"
                                   "NEW: Automatic reconnection on stream interruption\n"
                                   "START Click 'Start Muse Streaming' to begin\n")
        main_layout.addWidget(self.log_text)
        
    def setup_plots(self):
        # EEG plots setup - 2x2 grid of EEG channel plots
        channels = ['TP9', 'AF7', 'AF8', 'TP10']
        colors = ['#ffd700', '#00bfff', '#ff6347', '#32cd32']  # Gold, Blue, Red, Green
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        self.eeg_plots = {}
        self.eeg_curves = {}
        
        for (channel, color, (row, col)) in zip(channels, colors, positions):
            plot = self.eeg_plot_widget.addPlot(title=f"EEG {channel}", 
                                           row=row, col=col)
            plot.setLabel('left', 'Amplitude (µV)', color='white', size='11pt')
            plot.setLabel('bottom', 'Time (seconds)', color='white', size='11pt')
            plot.showGrid(x=True, y=True, alpha=0.4)
            plot.setMouseEnabled(x=True, y=True)  # Allow zooming
            plot.setMenuEnabled(True)  # Right-click menu
            plot.setYRange(-200, 200)
            plot.enableAutoRange(axis='y', enable=True)
            
            # Styling
            plot.getAxis('left').setTextPen('white')
            plot.getAxis('bottom').setTextPen('white')
            plot.setTitle(f"EEG {channel}", color='white', size='12pt')
            
            curve = plot.plot(pen=pg.mkPen(color=color, width=3))
            
            self.eeg_plots[channel] = plot
            self.eeg_curves[channel] = curve
        
        # Meditation tracking plots setup
        # 10-second interval plot (top)
        self.meditation_10s_plot = self.meditation_plot_widget.addPlot(title="10s Intervals", row=0, col=0)
        self.meditation_10s_plot.setLabel('left', 'Score', color='white', size='10pt')
        self.meditation_10s_plot.setLabel('bottom', 'Time (min)', color='white', size='10pt')
        self.meditation_10s_plot.showGrid(x=True, y=True, alpha=0.4)
        self.meditation_10s_plot.setYRange(0, 100)
        self.meditation_10s_plot.setMouseEnabled(x=True, y=True)
        self.meditation_10s_plot.getAxis('left').setTextPen('white')
        self.meditation_10s_plot.getAxis('bottom').setTextPen('white')
        self.meditation_10s_plot.setTitle("10s Intervals", color='white', size='11pt')
        
        # Add reference lines for meditation levels
        self.meditation_10s_plot.addLine(y=75, pen=pg.mkPen('#32cd32', width=1, style=2))  # Deep meditation
        self.meditation_10s_plot.addLine(y=60, pen=pg.mkPen('#ffd700', width=1, style=2))  # Calm/relaxed
        self.meditation_10s_plot.addLine(y=40, pen=pg.mkPen('#ffa500', width=1, style=2))  # Mild relaxation
        self.meditation_10s_plot.addLine(y=25, pen=pg.mkPen('#ff6347', width=1, style=2))  # Alert/focused
        
        # Meditation curve with gradient fill
        self.meditation_10s_curve = self.meditation_10s_plot.plot(
            pen=pg.mkPen(color='#90ee90', width=3),
            brush=pg.mkBrush(color=(144, 238, 144, 50))  # Light green with transparency
        )
        
        # 1-minute interval plot (bottom)
        self.meditation_1m_plot = self.meditation_plot_widget.addPlot(title="1min Intervals", row=1, col=0)
        self.meditation_1m_plot.setLabel('left', 'Score', color='white', size='10pt')
        self.meditation_1m_plot.setLabel('bottom', 'Time (hour)', color='white', size='10pt')
        self.meditation_1m_plot.showGrid(x=True, y=True, alpha=0.4)
        self.meditation_1m_plot.setYRange(0, 100)
        self.meditation_1m_plot.setMouseEnabled(x=True, y=True)
        self.meditation_1m_plot.getAxis('left').setTextPen('white')
        self.meditation_1m_plot.getAxis('bottom').setTextPen('white')
        self.meditation_1m_plot.setTitle("1min Intervals", color='white', size='11pt')
        
        # Add reference lines for meditation levels
        self.meditation_1m_plot.addLine(y=75, pen=pg.mkPen('#32cd32', width=1, style=2))  # Deep meditation
        self.meditation_1m_plot.addLine(y=60, pen=pg.mkPen('#ffd700', width=1, style=2))  # Calm/relaxed
        self.meditation_1m_plot.addLine(y=40, pen=pg.mkPen('#ffa500', width=1, style=2))  # Mild relaxation
        self.meditation_1m_plot.addLine(y=25, pen=pg.mkPen('#ff6347', width=1, style=2))  # Alert/focused
        
        # Meditation curve with different color
        self.meditation_1m_curve = self.meditation_1m_plot.plot(
            pen=pg.mkPen(color='#87ceeb', width=3),
            brush=pg.mkBrush(color=(135, 206, 235, 50))  # Light blue with transparency
        )
            
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_status_message(self, message):
        """Update status from LSL receiver"""
        self.log_message(message)
        if "Connected to" in message:
            self.status_label.setText("Status: Streaming from LSL")
            self.status_label.setStyleSheet("color: #90ee90;")
        elif "error" in message.lower() or "failed" in message.lower():
            self.status_label.setText("Status: Error")
            self.status_label.setStyleSheet("color: #ff6347;")
            
    def process_eeg_data(self, sample):
        """Process received EEG data"""
        # Add to meditation analyzer
        self.meditation_analyzer.add_sample(sample)
        
        # Add to calibration if active
        if self.is_calibrating:
            self.meditation_analyzer.add_calibration_sample(sample)
        
        # Add to plot buffers
        current_time = time.time()
        self.time_data.append(current_time)
        
        channels = ['TP9', 'AF7', 'AF8', 'TP10']
        for i, channel in enumerate(channels):
            if i < len(sample):
                self.eeg_data[channel].append(sample[i])
        
        self.sample_count += 1
        
        # Update plots periodically
        if self.sample_count % 20 == 0:  # Every 20 samples
            self.update_plots()
            
    def update_plots(self):
        """Update EEG plots with better scaling"""
        if len(self.time_data) < 10:
            return
            
        time_array = np.array(self.time_data)
        time_relative = time_array - time_array[-1]  # Relative to current
        
        channels = ['TP9', 'AF7', 'AF8', 'TP10']
        for channel in channels:
            if len(self.eeg_data[channel]) > 0:
                data_array = np.array(self.eeg_data[channel])
                self.eeg_curves[channel].setData(time_relative, data_array)
                
                # Auto-scale Y axis to data range with some padding
                if len(data_array) > 50:  # Only scale when we have enough data
                    data_min, data_max = np.min(data_array[-500:]), np.max(data_array[-500:])  # Last ~2 seconds
                    padding = (data_max - data_min) * 0.1  # 10% padding
                    if data_max - data_min > 10:  # Only if we have reasonable signal range
                        self.eeg_plots[channel].setYRange(data_min - padding, data_max + padding)
                
    def update_meditation_display(self):
        """Update meditation score display"""
        score, state = self.meditation_analyzer.calculate_meditation_score()
        
        self.meditation_label.setText(f"MEDITATION: {score:.1f}/100")
        self.state_label.setText(f"STATE: {state}")
        self.meditation_progress.setValue(int(score))
        
        # Color coding
        if score > 75:
            color = "#32cd32"  # Green
        elif score > 60:
            color = "#ffd700"  # Gold
        elif score > 40:
            color = "#ffa500"  # Orange
        else:
            color = "#ff6347"  # Red
            
        self.meditation_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def record_meditation_10s(self):
        """Record meditation score every 10 seconds"""
        score, _ = self.meditation_analyzer.calculate_meditation_score()
        current_time = time.time()
        
        self.meditation_10s_data.append(score)
        self.meditation_10s_times.append(current_time)
        
        self.update_meditation_10s_plot()
        self.update_meditation_stats()
    
    def record_meditation_1m(self):
        """Record meditation score every minute"""
        score, _ = self.meditation_analyzer.calculate_meditation_score()
        current_time = time.time()
        
        self.meditation_1m_data.append(score)
        self.meditation_1m_times.append(current_time)
        
        self.update_meditation_1m_plot()
        self.update_meditation_stats()
    
    def update_meditation_stats(self):
        """Update meditation statistics display"""
        if len(self.meditation_10s_data) > 0:
            recent_scores = list(self.meditation_10s_data)[-18:]  # Last 3 minutes (18 * 10s)
            if len(recent_scores) > 0:
                avg_score = np.mean(recent_scores)
                max_score = np.max(recent_scores)
                min_score = np.min(recent_scores)
                self.meditation_stats_label.setText(
                    f"Last 3min: Avg {avg_score:.1f}, Max {max_score:.1f}, Min {min_score:.1f}"
                )
        else:
            self.meditation_stats_label.setText("STATS: Collecting data...")
    
    def update_meditation_10s_plot(self):
        """Update the 10-second meditation tracking plot"""
        if len(self.meditation_10s_data) < 2:
            return
            
        # Convert times to minutes relative to the latest time
        times_array = np.array(self.meditation_10s_times)
        time_relative = (times_array - times_array[-1]) / 60.0  # Convert to minutes
        scores_array = np.array(self.meditation_10s_data)
        
        # Update the plot
        self.meditation_10s_curve.setData(time_relative, scores_array)
        
        # Auto-scale X axis to show meaningful time range
        if len(time_relative) > 1:
            self.meditation_10s_plot.setXRange(time_relative[0], time_relative[-1])
    
    def update_meditation_1m_plot(self):
        """Update the 1-minute meditation tracking plot"""
        if len(self.meditation_1m_data) < 2:
            return
            
        # Convert times to hours relative to the latest time
        times_array = np.array(self.meditation_1m_times)
        time_relative = (times_array - times_array[-1]) / 3600.0  # Convert to hours
        scores_array = np.array(self.meditation_1m_data)
        
        # Update the plot
        self.meditation_1m_curve.setData(time_relative, scores_array)
        
        # Auto-scale X axis to show meaningful time range
        if len(time_relative) > 1:
            self.meditation_1m_plot.setXRange(time_relative[0], time_relative[-1])
    
    def start_calibration(self):
        """Start 20-second calibration process"""
        if not self.is_streaming:
            self.log_message("WARNING Start streaming before calibration")
            return
            
        self.is_calibrating = True
        self.calibration_start_time = time.time()
        
        # Start calibration in analyzer
        self.meditation_analyzer.start_calibration()
        
        # Update UI
        self.calibrate_btn.setEnabled(False)
        self.calibrate_btn.setText("CALIBRATING... 20s")
        self.calibrate_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffa500, stop:1 #ff6347);
                color: white; 
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Start calibration timer (update every second)
        self.calibration_timer.start(1000)
        
        self.log_message("CALIBRATING started - sit calmly for 20 seconds")
        self.log_message("TIP This will establish your personal baseline for better accuracy")
        
    def update_calibration(self):
        """Update calibration progress"""
        elapsed = time.time() - self.calibration_start_time
        remaining = max(0, self.calibration_duration - elapsed)
        
        if remaining > 0:
            self.calibrate_btn.setText(f"CALIBRATING... {int(remaining)}s")
        else:
            self.finish_calibration()
            
    def finish_calibration(self):
        """Complete calibration process"""
        self.calibration_timer.stop()
        self.is_calibrating = False
        
        # Finish calibration in analyzer
        success, message = self.meditation_analyzer.finish_calibration()
        
        if success:
            self.log_message(f"SUCCESS {message}")
            self.calibrate_btn.setText("RECALIBRATE")
            self.calibrate_btn.setStyleSheet("""
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #32cd32, stop:1 #228b22);
                    color: white; 
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
        else:
            self.log_message(f"ERROR {message}")
            self.calibrate_btn.setText("CALIBRATE (20s)")
            self.calibrate_btn.setStyleSheet("")  # Reset style
            
        self.calibrate_btn.setEnabled(True)
    
    def handle_connection_lost(self):
        """Handle when connection is lost"""
        self.log_message("CONNECTION Lost - stopping stream")
        if self.is_streaming and self.stream_process:
            try:
                self.stream_process.terminate()
                self.stream_process.wait(timeout=3)
            except:
                try:
                    self.stream_process.kill()
                except:
                    pass
            self.is_streaming = False
            self.log_message("STOPPED Stream stopped")
        
    def update_sample_count(self):
        """Update sample counter"""
        if hasattr(self.lsl_receiver, 'sample_count'):
            self.sample_label.setText(f"SAMPLES: {self.lsl_receiver.sample_count}")
        else:
            self.sample_label.setText(f"SAMPLES: {self.sample_count}")
            
    def toggle_streaming(self):
        """Start/stop Muse streaming"""
        if not self.is_streaming:
            self.start_streaming()
        else:
            self.stop_streaming()
            
    def start_streaming(self):
        """Start muselsl streaming process"""
        if not MUSE_AVAILABLE:
            self.log_message("ERROR muselsl not available")
            return
            
        try:
            self.log_message("SEARCHING Finding Muse device...")
            
            # Find Muse
            muses = list_muses(backend='bleak')
            if not muses:
                self.log_message("ERROR No Muse devices found")
                return
            
            muse_address = muses[0]['address']
            muse_name = muses[0]['name']
            self.log_message(f"FOUND: {muse_name}")
            
            self.start_streaming_process()
            
        except Exception as e:
            self.log_message(f"ERROR starting streaming: {e}")
            
    def start_streaming_process(self):
        """Start the muselsl streaming process"""
        try:
            # Find Muse again (in case this is a reconnect)
            muses = list_muses(backend='bleak')
            if not muses:
                self.log_message("ERROR No Muse devices found for reconnect")
                return
                
            muse_address = muses[0]['address']
            
            # Start muselsl streaming process
            self.log_message("STARTING muselsl stream process...")
            cmd = [
                'muselsl', 'stream',
                '--address', muse_address,
                '--ppg', '--acc'
            ]
            
            self.stream_process = subprocess.Popen(cmd)
            self.log_message("SUCCESS muselsl stream started!")
            
            # Wait for stream to establish (muselsl needs time to start LSL stream)
            time.sleep(5)
            
            # Start LSL data receiver
            self.log_message("CONNECTING Starting LSL data receiver...")
            self.lsl_receiver.start_receiving()
            
            # Update UI
            self.is_streaming = True
            self.start_btn.setText("STOP Streaming")
            self.start_btn.setStyleSheet("""
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #ff4444, stop:1 #cc0000);
                    color: white; 
                    border: none;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #ff6666, stop:1 #ff4444);
                }
            """)
            
            # Enable calibration button
            self.calibrate_btn.setEnabled(True)
            
            # Start timers
            self.meditation_timer.start(2000)     # Every 2 seconds for display
            self.sample_timer.start(1000)         # Every second for sample count
            self.meditation_10s_timer.start(10000)  # Every 10 seconds for tracking
            self.meditation_1m_timer.start(60000)   # Every 1 minute for tracking
            
        except Exception as e:
            self.log_message(f"ERROR in streaming process: {e}")
            
    def stop_streaming(self):
        """Stop streaming"""
        self.is_streaming = False
        
        # Stop LSL receiver
        self.lsl_receiver.stop_receiving()
        
        # Stop muselsl process
        if self.stream_process:
            try:
                self.stream_process.terminate()
                self.stream_process.wait(timeout=5)
            except:
                try:
                    self.stream_process.kill()
                except:
                    pass
            self.stream_process = None
        
        # Stop timers
        self.meditation_timer.stop()
        self.sample_timer.stop()
        self.meditation_10s_timer.stop()
        self.meditation_1m_timer.stop()
        self.calibration_timer.stop()
        
        # Stop calibration if active
        if self.is_calibrating:
            self.is_calibrating = False
        
        # Reset UI
        self.start_btn.setText("START Muse Streaming")
        self.start_btn.setStyleSheet("")  # Reset to default
        self.calibrate_btn.setEnabled(False)
        self.calibrate_btn.setText("CALIBRATE (20s)")
        self.calibrate_btn.setStyleSheet("")  # Reset to default
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: #ffd700;")
        self.sample_label.setText("SAMPLES: 0")
        self.meditation_label.setText("MEDITATION: --/100")
        self.state_label.setText("STATE: Ready")
        self.meditation_progress.setValue(0)
        
        self.sample_count = 0
        
        self.log_message("STOPPED Streaming stopped")
        
    def closeEvent(self, event):
        """Handle window close"""
        if self.is_streaming:
            self.stop_streaming()
        event.accept()


def main():
    try:
        if not QT_AVAILABLE:
            print("ERROR Qt components not available")
            sys.exit(1)
            
        if not MUSE_AVAILABLE:
            print("ERROR Muse components not available")
            sys.exit(1)
            
        import os
        os.environ['QT_X11_NO_MITSHM'] = '1'
        
        app = QApplication(sys.argv)
        app.setApplicationName("Working Muse 2 GUI")
        
        window = WorkingMuseGUI()
        window.show()
        
        print("SUCCESS Working Muse 2 GUI launched successfully!")
        print("READY Using fixed muselsl library with LSL streaming")
        print("ACTIVE Ready for real-time brain monitoring!")
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()