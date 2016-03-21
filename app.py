from flask import Flask
import peewee
#from flask.ext.stormpath import StormpathManager

app = Flask(__name__)
app.config.from_object('settings')
#stormpath_manager = StormpathManager(app)

db = peewee.MySQLDatabase(app.config["DATABASE_NAME"],
                          host=app.config["DATABASE_HOST"],
                          user=app.config["DATABASE_USER"],
                          passwd=app.config["DATABASE_PASSWORD"])

db.set_autocommit(False)