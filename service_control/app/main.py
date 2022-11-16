import uvicorn
from threading import Thread

from settings import settings
from db_copy import copy_db
from app import app

if __name__ == "__main__":

    parser_thread = Thread(
        target=copy_db,
        args=(),
        daemon=True,
    ).start()

    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
    )



