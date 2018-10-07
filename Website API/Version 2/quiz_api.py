import flask
from numpy import random
#from flaskext.mysql import MySQL
from flask import request, make_response
import random
import string

DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

code_list = list()

VOTES = {
    "7": [0, 0],
    "8": [0, 0],
    "9": [0, 0],
    "10": [0, 0],
    "11": [0, 0],
    "12": [0, 0],
    "13": [0, 0],
}

VOTING_READY = False # Need API to toggle voting

@APP.route('/', methods=['GET', 'POST'])
def index():
    """Home Page"""
    # password = request.args.get('password')
    if 'adminUser' in request.cookies:
        # Return ADMIN control panel
        return
    else:
        # Return getCode
        return flask.redirect(flask.url_for('getCode'))

@APP.route('/admin', methods=['GET', 'POST'])
def admin():
    passwordFailed = request.args.get('passwordFailed')
    if passwordFailed:
        return flask.render_template("admin_login.html", passwordFailed=True)
    else:
        return flask.render_template("admin_login.html")

@APP.route('/getAdmin', methods=['GET', 'POST'])
def getAdmin():
    inputted_password = request.form['passwordField']
    if inputted_password != "test_password": # Super secure password, btw
        return flask.redirect(flask.url_for('admin', passwordFailed=True))

    return "SUCC" # Admin Panel


def create_code():
    global code_list
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    while code in code_list:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code_list.append(code)
    return code

@APP.route('/getCode', methods=['GET', 'POST'])
def getCode():
    if 'userCode' in request.cookies:
        response = flask.make_response(flask.redirect(flask.url_for('getYear')))
        # response.set_cookie('hasCode', "1")
        # response.set_cookie('userCode', request.cookies.get('userCode'))
    else:
        generated_code = create_code()
        # response = flask.make_response(flask.render_template("index.html", code=str(generated_code)))
        response = flask.make_response(flask.redirect(flask.url_for('getYear')))
        # response.set_cookie('hasCode', "1")
        response.set_cookie('userCode', generated_code)
    return response

@APP.route('/getYear', methods=['GET', 'POST'])
def getYear():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('panel'))

    return flask.render_template('yearForm.html', code=request.cookies.get('userCode'))

@APP.route('/yearForm', methods=['GET', 'POST'])
def yearForm():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('panel'))

    year = request.form['selectYear']

    response = flask.redirect(flask.url_for('panel'))
    response.set_cookie('userGroup', year)
    return response

@APP.route('/panel', methods=['GET', 'POST'])
def panel():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    return "I LIKE TO HANG OUT WITH MY DOG"


if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=80, debug=DEBUG)