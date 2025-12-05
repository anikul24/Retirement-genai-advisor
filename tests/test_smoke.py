# tests/test_smoke.py
from streamlit.testing.v1 import AppTest

def test_app_startup():
    """Smoke Test: Does the app boot up without crashing?"""
    # Load the app file
    at = AppTest.from_file("src/app.py")
    
    # Mock secrets to prevent real API calls during smoke tests
    at.secrets["OPENAI_API_KEY"] = "sk-fake-key-for-testing"
    at.secrets["PINECONE_API_KEY"] = "fake-pinecone-key"
    
    # Run the app script
    at.run(timeout=30)
    
    # Assert no exceptions were thrown
    assert not at.exception
    
    # Check if key UI elements exist
    assert len(at.title) > 0
    assert at.title[0].value == "GenAI Retirement Advisor"

