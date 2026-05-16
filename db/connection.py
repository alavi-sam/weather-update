from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
load_dotenv()


db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_port = os.getenv("DB_PORT")
db_host = os.getenv("DB_HOST")
db_password = os.getenv("DB_PASS")

db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)
