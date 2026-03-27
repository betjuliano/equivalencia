# Backend runner
import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=3008, reload=True)
