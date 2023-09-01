from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.normpath(".env"))

class Config:
    API_TOKEN: str = Field(..., env='API_TOKEN')
    MDGT_CHAT_ID: str = Field(..., env='MDGT_CHAT_ID')
    MDGT_CHANNEL_ID: str = Field(..., env='MDGT_CHANNEL_ID')
    SERVER_URI: str = Field(..., env='SERVER_URI')
    SERVER_CUSTOMER_URI: str = Field(..., env='SERVER_CUSTOMER_URI')

configs = Config()