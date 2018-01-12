#!/usr/bin/python
from __future__ import print_function

import os
import requests
import jmespath
from flask import Response, redirect, url_for, flash, render_template
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

# Local imports
from app import app, db
from auth import OAuthSignIn
from models import User
import api_routes


#===============================================================================
# Setup
#===============================================================================

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id==user_id)


#===============================================================================
# Application routes
#===============================================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In')

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')

@app.route('/users')
@login_required
def users():
    return render_template('users.html', title='Users')

@app.route('/donors')
@login_required
def donors():
    return render_template('donors.html', title='Donors')

@app.route('/samples')
@login_required
def samples():
    return render_template('samples.html', title='Samples')

@app.route('/import')
@login_required
def import_data_hub():
    return render_template('import.html', title='Import Data Hub')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html', title='Sign In')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/<path:path>')
def plain_html(path):
    return app.send_static_file(path)


#===============================================================================
# OAuth routes
#===============================================================================

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('home'))

    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()

    # Need a valid email address for user identification
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))

    # Look if the user already exists
    user = None
    try:
        user = User.get(User.email==email)
    except:
        # User has not been created/authorized
        print('User not found: %s, %s' % (username, email))
        flash('User not registered')
        return redirect(url_for('index'))

    # First time the user logs in, we save the name
    if user and user.name is None:
        # Create the user. Try and use their name returned by Google,
        # but if it is not set, split the email address at the @.
        if username is None or username == "":
            username = email.split('@')[0]

        user.name = username
        user.save()

    # Then, log in
    login_user(user)

    # Finally, send the user to the main interface
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=app.config["APPLICATION_DEBUG_MODE"],
            port=app.config["APPLICATION_PORT"],
            host=app.config["APPLICATION_HOST"])
