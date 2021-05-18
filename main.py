from app.main import app
from app.main import create_database

if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0")
