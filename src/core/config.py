import os
from dotenv import load_dotenv

load_dotenv(os.path.abspath(__file__ + "/../../../.env"))

API_V1_PREFIX = os.environ.get('API_V1_PREFIX', '/api/v1')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Mirea Ninja Voice Helper Backend')

SCHEDULE_API_URL = os.environ.get('SCHEDULE_API_URL')

YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')
VK_API_KEY = os.environ.get('VK_API_KEY')
SBER_API_KEY = os.environ.get('SBER_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
SIRI_API_KEY = os.environ.get('SIRI_API_KEY')