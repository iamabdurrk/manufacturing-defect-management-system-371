"""Backend server entrypoint.

Runs the Flask app for the Manufacturing Defect Management System.
"""

from __future__ import annotations

import os

from app.app_factory import create_app

app = create_app()

if __name__ == "__main__":
    # Bind to PORT for container environment; default to 3001 to match frontend dev.
    port = int(os.environ.get("PORT", "3001"))
    app.run(host="0.0.0.0", port=port, debug=False)
