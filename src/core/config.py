import os
from dotenv import load_dotenv

load_dotenv(os.path.abspath(__file__ + "/../../../.env"))

API_V1_PREFIX = os.environ.get('API_V1_PREFIX', '/api/v1')
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'Mirea Ninja Voice Helper Backend')

SCHEDULE_API_URL = os.environ.get('SCHEDULE_API_URL')

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_PORT = os.environ.get('DATABASE_PORT')

SKILL_ID = os.environ.get('SKILL_ID')
VK_API_KEY = os.environ.get('VK_API_KEY')