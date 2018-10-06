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
    year = request.form['selectYear']
    response = flask.make_response(flask.render_template('vote.html'))
    response.set_cookie('yearGroup', year)
    return response

@APP.route('/', methods=['GET', 'POST'])
def index():
    """Home Page"""
    return flask.render_template("index.html")

if __name__ == "__main__":
    APP.run(host="192.168.1.205", port=80, debug=DEBUG)
