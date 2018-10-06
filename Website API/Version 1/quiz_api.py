import flask
from flaskext.mysql import MySQL
from flask import request, make_response

DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

TOTAL_VOTES = [0, 0]


@APP.route('/votea', methods=['GET', 'POST'])
def votea():
    TOTAL_VOTES[0] += 1
    return flask.render_template("voted_a.html")


@APP.route('/voteb', methods=['GET', 'POST'])
def voteb():
    TOTAL_VOTES[1] += 1
    return flask.render_template("voted_b.html")


@APP.route('/unvote_a', methods=['GET', 'POST'])
def unvote_a():
    TOTAL_VOTES[0] -= 1
    return flask.redirect(flask.url_for("index"))


@APP.route('/unvote_b', methods=['GET', 'POST'])
def unvote_b():
    TOTAL_VOTES[1] -= 1
    return flask.redirect(flask.url_for("index"))


@APP.route('/', methods=['GET', 'POST'])
def index():
    """Home Page"""
    return flask.render_template("vote.html")


if __name__ == "__main__":
    APP.run(port=80, debug=DEBUG)
