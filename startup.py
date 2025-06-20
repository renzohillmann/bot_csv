import os
import sys
from pathlib import Path


# Import the aiohttp app
from app import init_app

# This is used by Azure Web App to start the application
app = init_app()