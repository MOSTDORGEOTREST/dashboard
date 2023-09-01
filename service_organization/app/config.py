from pydantic import BaseSettings, Field
import os
from dotenv import load_dotenv
import http.client

load_dotenv(dotenv_path=os.path.normpath(".env"))

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

class Configs_docker_compose(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
    jwt_expiration: int = Field(..., env='JWT_EXPIRATION')

configs = Configs_docker_compose()
