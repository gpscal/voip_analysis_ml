import os

class Config:
    # Set directories relative to the application directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'DATA_DIR')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'OUTPUT')
    MODEL_PATH = os.path.join(BASE_DIR, 'MODELS/voip_quality_model.pkl')
