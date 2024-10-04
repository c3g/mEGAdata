import requests
import logging
import json

import globals
import utils

# Log in
def login():
    path = "/login"
    payload = {"username": f"{globals.config['login']['username']}", "password": f"{globals.config['login']['password']}", "loginType": "submitter"}
    r = requests.post(globals.BASE_URL + path, data=payload)
    if r.status_code != 200:
        raise Exception("Check login credentials")
    # Save login token to settings.
    json_response = r.json()
    globals.config["login"]["token"] = json_response["response"]["result"][0]["session"]["sessionToken"]
    logging.debug(f"Logged in with token {globals.config['login']['token']}.")
    utils.write_config()

# Log out
def logout():
    path = "/logout"
    url = globals.BASE_URL + path
    r = requests.delete(url, headers=json.loads(globals.config["global"]["headers"]))
    if r.status_code != 200:
        raise Exception("Cannot log out.")
    logging.debug(f"Logged out.")
