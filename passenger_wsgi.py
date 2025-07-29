import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(__file__))

from app import app as application
