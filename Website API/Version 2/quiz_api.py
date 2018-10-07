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
    if 'userAdmin' in request.cookies:
        # Return ADMIN control panel
        return flask.redirect(flask.url_for('adminPanel'))
    else:
        return flask.redirect(flask.url_for('normalUser'))

@APP.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'userAdmin' in request.cookies:
        return flask.redirect(flask.url_for('adminPanel'))

    passwordFailed = request.args.get('passwordFailed')
    notLoggedIn = request.args.get('notLoggedIn')
    if passwordFailed:
        return flask.render_template("adminLogin.html", passwordFailed=True)
    
    if notLoggedIn:
        return flask.render_template('adminLogin.html', notLoggedIn=True)

    return flask.render_template("adminLogin.html")

@APP.route('/normalUser', methods=['GET', 'POST'])
def normalUser():
    global code_list
    if 'userCode' in request.cookies:
        if request.cookies.get('userCode') in code_list:
            flask.redirect(flask.url_for('home'))
        else:
            code_list.append(request.cookies.get('userCode'))

    return flask.redirect(flask.url_for('getCode'))

@APP.route('/getAdmin', methods=['GET', 'POST'])
def getAdmin():
    inputted_password = request.form['passwordField']
    if inputted_password != "test_password": # Super secure password, btw
        return flask.redirect(flask.url_for('admin', passwordFailed=True))
    response = flask.make_response(flask.redirect(flask.url_for('adminPanel')))
    response.set_cookie('userAdmin', '1')
    return response

@APP.route('/adminPanel', methods=['GET', 'POST'])
def adminPanel():
    if not 'userAdmin' in request.cookies:
        return flask.redirect(flask.url_for('admin', notLoggedIn=True))

    return flask.render_template("adminPanel.html", userCount=str(len(code_list)))

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
        return flask.redirect(flask.url_for('home'))

    return flask.render_template('yearForm.html', code=request.cookies.get('userCode'))

@APP.route('/yearForm', methods=['GET', 'POST'])
def yearForm():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('home'))

    year = request.form['selectYear']

    response = flask.redirect(flask.url_for('home'))
    response.set_cookie('userGroup', year)
    return response

@APP.route('/home', methods=['GET', 'POST'])
def home():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))
    
    return flask.render_template('home.html', code=request.cookies.get('userCode'),
                            year=request.cookies.get("userGroup"))

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=80, debug=DEBUG)