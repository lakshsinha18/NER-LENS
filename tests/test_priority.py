from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.services.priority import priority_for


def test_priority_increases_with_exposure():
    low = priority_for(70, 1, 1, 1, 1)
    high = priority_for(70, 1.4, 1.4, 1.3, 1.2)
    assert high["priority_score"] > low["priority_score"]
