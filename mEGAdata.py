#!/usr/bin/python

from app import app, db
import requests
from flask import Response
import jmespath
import os

# Local imports
from queries import *
import api_routes

#===============================================================================
# Application routes
#===============================================================================
@app.route("/")
# @groups_required(['edit'])
# @login_required
def root():
    return app.send_static_file("index.html")


@app.route('/<path:path>')
# @login_required
def plain_html(path):
    return app.send_static_file(path)



if __name__ == "__main__":
    app.run(debug=app.config["APPLICATION_DEBUG_MODE"], port=app.config["APPLICATION_PORT"], host=app.config["APPLICATION_HOST"])
