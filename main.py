from app import create_app
from config import PORT, HOST
from app.utilities.logger import logger

# Creating the app
app = create_app()

if __name__ == '__main__':

    logger.info(f"App started successfully on - {HOST}:{PORT}")

    # Running the app
    app.run(host=HOST, port=PORT)
