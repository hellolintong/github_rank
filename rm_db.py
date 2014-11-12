from mongoengine import connect
from config import Config

db = connect(Config.DB_NAME, host = Config.DB_HOST, port = Config.DB_PORT)
db.drop_database(Config.DB_NAME)
