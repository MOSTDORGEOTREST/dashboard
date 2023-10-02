import os

class Config:
    API_TOKEN: str = os.environ['API_TOKEN']
    MDGT_CHAT_ID: str = os.environ['MDGT_CHAT_ID']
    MDGT_CHANNEL_ID: str = os.environ['MDGT_CHANNEL_ID']
    SERVER_URI: str = os.environ['SERVER_URI']
    SERVER_CUSTOMER_URI: str = os.environ['SERVER_CUSTOMER_URI']

configs = Config()
