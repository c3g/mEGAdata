from flask import Flask
import peewee

app = Flask(__name__)
app.config.from_object('settings')

db = peewee.MySQLDatabase(app.config["DATABASE_NAME"],
                          host=app.config["DATABASE_HOST"],
                          user=app.config["DATABASE_USER"],
                          passwd=app.config["DATABASE_PASSWORD"])

db.set_autocommit(False)