from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from pcs_verify import pcs_verify
import os
from werkzeug.security import check_password_hash

# Flask
app = Flask(__name__)

# PCS Forum
users = {}


@app.route('/')
def index():
    if g.user:
        return redirect(url_for('profile', username=g.user))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None

        if username not in users:
            error = 'Incorrect username.'
        elif not check_password_hash(users[username]['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = username

            flash("Welcome back, {}!".format(users[username]['name']), 'success')

            return redirect(url_for('profile', username=username))

        flash(error, 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()

    flash("You have been logged out successfully.", 'success')

    return redirect(url_for('index'))


@app.route('/profile/<username>')
def profile(username):
    if username not in users:
        flash("The username does not exist!", 'danger')
        return redirect(url_for('index'))

    user = users[username]

    return render_template(
        'profile.html',
        username=username,
        name=user['name'],
        avatar=user['avatar'],
        slogan=user['slogan'],
        description=user['description']
    )


@app.route('/profile/<username>/edit', methods=('GET', 'POST'))
def edit_profile(username):
    if not g.user or g.user != username:
        flash("You don't have permission to edit this profile!", 'danger')
        return redirect(url_for('profile', username=username))

    if request.method == 'POST':
        if 'slogan' in request.form:
            users[username]['slogan'] = request.form['slogan']

        if 'description' in request.form:
            users[username]['description'] = request.form['description']

        flash("Your profile has been updated!", 'success')

        return redirect(url_for('profile', username=username))

    user = users[username]

    return render_template(
        'edit_profile.html',
        username=username,
        name=user['name'],
        avatar=user['avatar'],
        slogan=user['slogan'],
        description=user['description']
    )


@app.before_request
def before_request():
    username = session.get('username')

    if username is None:
        g.user = None
    else:
        g.user = username

    g.users = {key: value['name'] for key, value in users.items()}


@app.route('/verify', methods=('GET', 'POST'))
def verify():
    code = ''

    if request.method == 'POST':
        if 'code' not in request.form or request.form['code'] == '':
            flash("Can't load your code.", 'danger')
            return render_template('verify.html')

        code = request.form['code']

        global users
        users = default_user_info()

        status, message = pcs_verify(users, code)

        flash(message, 'success' if status else 'danger')

    return render_template('verify.html', code=code)


@app.route('/reset')
def reset():
    global users
    users = default_user_info()

    flash("All profiles have been reset!", "success")

    return redirect(url_for('index'))


def default_user_info():
    return {
        'catrina': {
            'username': 'catrina',
            'password': 'pbkdf2:sha256:150000$sd8iXVUr$6882dfebceb7ce71a242667fdec076bc93e33b22d42e51edf3cb9fe1d454c501',
            'name': 'Catrina',
            'avatar': '8918ce317a7726255b37fe972a423c3b',
            'slogan': 'Hi, my name is Catrina!',
            'description': ''
        },
        'hugh': {
            'username': 'hugh',
            'password': 'pbkdf2:sha256:150000$UphSisaZ$5ed91664ffa2c8e4dee9844045902f43b8bc47c0491ba482b24ed573dfb93737',
            'name': 'Hugh',
            'avatar': '491dbec39f772fb5ac326b6829faf542',
            'slogan': 'And my name is Hugh.',
            'description': ''
        },
        'sarah': {
            'username': 'sarah',
            'password': '',
            'name': 'Sarah',
            'avatar': 'b0afb5dba0df5de740d72f14c22ea075',
            'slogan': 'I am Sarah!',
            'description': ''
        },
        'emma': {
            'username': 'emma',
            'password': '',
            'name': 'Emma',
            'avatar': '421a669761c59f3278735113941a55c0',
            'slogan': 'I am Emma!',
            'description': ''
        },
        'joe': {
            'username': 'joe',
            'password': '',
            'name': 'Joe',
            'avatar': '10fc31fcdefb8126b67fd3a5404ce65a',
            'slogan': 'And I am Joe to you.',
            'description': ''
        },
        'samy': {
            'username': 'samy',
            'password': '',
            'name': 'Samy',
            'avatar': '3bc011b83a83224e97ee34fdd8fe35ea',
            'slogan': '',
            'description': ''
        }
    }


if __name__ == '__main__':
    users = default_user_info()
    app.config['SECRET_KEY'] = os.urandom(16)
    app.config['SESSION_COOKIE_NAME'] = 'pcs'
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.run(host="0.0.0.0", port=4000, debug=True)
