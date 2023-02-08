from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.normpath(".env"))

class Config:
    API_TOKEN = os.getenv('API_TOKEN')
    MDGT_CHAT_ID = os.getenv('MDGT_CHAT_ID')
    MDGT_CHANNEL_ID = os.getenv('MDGT_CHANNEL_ID')
    SERVER_URI = os.getenv('SERVER_URI')
    SERVER_CUSTOMER_URI = os.getenv('SERVER_CUSTOMER_URI')

configs = Config()