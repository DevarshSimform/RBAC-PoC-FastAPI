import os
import sys

from app.db.init_db import seed_initial_data

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


if __name__ == "__main__":
    seed_initial_data()
