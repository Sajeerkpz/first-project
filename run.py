import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend_py.app import create_app
from backend_py.config import SERVER_HOST, SERVER_PORT

app = create_app()

if __name__ == "__main__":
    print(f"Self Study Python Backend running at http://localhost:{SERVER_PORT}")
    print(f"API endpoints available at http://localhost:{SERVER_PORT}/api")
    print(f"Frontend viewable directly at http://localhost:{SERVER_PORT}/")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)

