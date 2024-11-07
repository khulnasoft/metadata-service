"""
Client for integration tests
"""

import warnings
from app.main import app
from fastapi.testclient import TestClient

# Moving to new client causes issues
warnings.filterwarnings("ignore", category=DeprecationWarning)
test_client = TestClient(app)
