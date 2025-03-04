# VoIP Analysis with Machine Learning

This project provides a web-based interface for analyzing VoIP communications using machine learning techniques. It includes functionality for analyzing PCAP files and training ML models for VoIP quality assessment.

## Project Structure

```
voip_analysis_ml/
├── app.py             # Main Flask application
|-- main.py
├── requirements.txt        # Project dependencies
├── uploads/               # Directory for temporary file uploads
├── templates/             # Flask HTML templates
│   ├── base.html         # Base template with common layout
│   ├── index.html        # Home page with upload forms
│   └── results.html      # Analysis results page
├── data_processing/       # Data processing modules
│   ├── __init__.py
│   ├── pcap_processor.py
├── ml_models/            # Machine learning modules
│   ├── __init__.py
│   ├── advanced_metrics.py
│   ├── feature_extraction.py
│   ├── model.py
│   ├── traffic_analyzer.py
│   └── train.py
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── config.py
│   └── logger.py
└── models/              # Directory to store trained models
    └── voip_quality_model.pkl
```

## Prerequisites

- Python3
- Flask
- Scapy
- NumPy
- scikit-learn
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gpscal/voip_analysis_ml.git
cd voip_analysis_ml
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

Run app.py file with command $ python3 app.py

Acess the web interface:
- Open your web browser and navigate to `http://localhost:5000`
- Use the "Analyze PCAP" form to analyze VoIP PCAP files
- Use the "Train Model" form to upload training data

## Features

- Web-based interface for VoIP analysis
- PCAP file upload and analysis
- Real-time visualization of analysis results
- Machine learning model training interface
- Comprehensive VoIP quality metrics including:
  - Mean Opinion Score (MOS)
  - Jitter analysis
  - Packet loss detection
  - Call flow analysis
  - Traffic pattern analysis

## Analysis Results

The application provides:
- Basic call statistics
- Quality metrics (MOS, jitter, packet loss)
- Traffic pattern analysis
- Protocol distribution
- Anomaly detection
- Interactive visualizations

## Development

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

Common issues and solutions:
- If you get permission errors, check directory permissions
- For import errors, verify your PYTHONPATH includes the project root
- For Flask errors, check the console output for detailed error messages

## Security Notes

For production deployment:
- Change debug mode to False
- Use a proper WSGI server
- Set up proper security measures
- Configure comprehensive logging
- Use environment variables for sensitive configuration

