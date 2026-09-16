"""pytest configuration for integration tests"""
import sys
from pathlib import Path

# Add implementation root to Python path so validators.registry can be imported
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
