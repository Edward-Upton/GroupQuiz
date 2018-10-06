import flask
from flaskext.mysql import MySQL
from flask import request, make_response

DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

VOTES = {
    "7": [0, 0],
    "8": [0, 0],
    "9": [0, 0],
    "10": [0, 0],
    "11": [0, 0],
    "12": [0, 0],
    "13": [0, 0],
}

VOTING_READY = False

@APP.route('/toggleVoting', methods=['GET'])
def toggleVoting():
    admin_user = request.args.get('username')
    if admin_user != 'mitgobla':
        return flask.redirect(flask.url_for('index'))
    global VOTING_READY
    if VOTING_READY:
        VOTING_READY = False
    else:
        VOTING_READY = True
    return "Voting Enabled: "+str(VOTING_READY)

@APP.route('/voted', methods=['POST'])
def voted():
    year = request.cookies.get('yearGroup')
    voteoption = request.form.to_dict(flat=False)
    if 'vote_a' in voteoption:
        VOTES[str(year)][0] += 1
        vote_value = "A"
    elif 'vote_b' in voteoption:
        VOTES[str(year)][1] += 1
        vote_value = "B"
    response = flask.make_response(flask.render_template('voted.html', vote_option=vote_value))
    response.set_cookie('yearGroup', year)
    return response


@APP.route('/submitYear', methods=['POST'])
def submitYear():
    """Submit Page"""
    if 'selectYear' in request.form:
        year = request.form['selectYear']
        voted = "N"
    else:
        year = request.cookies.get('yearGroup')
        voted = request.cookies.get('voted')

    if VOTING_READY:
        response = flask.make_response(flask.render_template('vote.html'))
    else:
        response = flask.make_response(flask.render_template('vote_notready.html'))
    response.set_cookie('yearGroup', year)
    response.set_cookie('voted', voted)
    return response

@APP.route('/', methods=['GET', 'POST'])
def index():
    """Home Page"""
    return flask.render_template("index.html")

if __name__ == "__main__":
    APP.run(host="192.168.1.205", port=80, debug=DEBUG)
