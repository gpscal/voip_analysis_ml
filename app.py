from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from main import process_voip_call
from data_processing.pcap_processor import extract_packets, filter_voip_packets
from ml_models.model import VoIPQualityModel
from ml_models.advanced_metrics import AdvancedVoIPMetrics
from ml_models.traffic_analyzer import VoIPTrafficAnalyzer
from utils.logger import setup_logger
from utils.config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup logger
logger = setup_logger()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pcap', 'pcapng'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Initialize analyzers
            quality_metrics = AdvancedVoIPMetrics()
            traffic_analyzer = VoIPTrafficAnalyzer()
            
            # Process PCAP
            packets = extract_packets(filepath)
            voip_packets = filter_voip_packets(packets)
            
            if not voip_packets:
                flash('No VoIP packets found in the file', 'error')
                return redirect(url_for('index'))
                
            # Analyze call
            call_data = process_voip_call(voip_packets)
            patterns = traffic_analyzer.extract_traffic_patterns(voip_packets)
            traffic_behavior = traffic_analyzer.analyze_traffic_behavior(patterns)
            flow_metrics = quality_metrics.analyze_call_flow(voip_packets)
            qos_report = quality_metrics.generate_qos_report(call_data, flow_metrics)
            
            # Clean up
            os.remove(filepath)
            
            return render_template('results.html', 
                                 call_data=call_data,
                                 qos_report=qos_report,
                                 traffic_behavior=traffic_behavior)
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            flash(f'Error analyzing file: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    flash('Invalid file type', 'error')
    return redirect(url_for('index'))

@app.route('/train', methods=['POST'])
def train():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Save file to Config.DATA_DIR for training
            data_dir = Config.DATA_DIR
            os.makedirs(data_dir, exist_ok=True)
            training_filepath = os.path.join(data_dir, filename)
            
            # Move file to training directory
            if os.path.exists(training_filepath):
                os.remove(training_filepath)  # Remove existing file if it exists
            os.rename(filepath, training_filepath)
            
            # Import and run training
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "train", 
                os.path.join(os.path.dirname(__file__), "ml_models", "train.py")
            )
            train_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(train_module)
            
            # Run training
            train_module.main()
            
            flash('Model training completed successfully', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            flash(f'Error training model: {str(e)}', 'error')
            return redirect(url_for('index'))
            
        finally:
            # Clean up files
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(training_filepath):
                os.remove(training_filepath)
    
    flash('Invalid file type', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
