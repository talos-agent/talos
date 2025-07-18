import sys
sys.path.insert(0, 'src')
from crypto_sentiment import main

def test_import():
    assert main is not None
