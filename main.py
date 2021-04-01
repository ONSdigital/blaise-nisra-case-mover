import os

from app.blaise_nisra_case_mover import app, load_config

load_config(app)

if __name__ == "__main__":
    port = os.getenv("5000")
    app.run(host="0.0.0.0", port=port)
