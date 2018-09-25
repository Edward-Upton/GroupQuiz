import flask
from flaskext.mysql import MySQL
from flask import request
DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

APP.config['MYSQL_DATABASE_USER'] = 'charityquiz'
APP.config['MYSQL_DATABASE_PASSWORD'] = 'charityday'
APP.config['MYSQL_DATABASE_DB'] = 'charities_day'
APP.config['MYSQL_DATABASE_HOST'] = 'localhost'

SQL = MySQL()
SQL.init_app(APP)

SQL_CONNECTION = SQL.connect()
SQL_CURSOR = SQL_CONNECTION.cursor()

TOTAL_VOTES = [0, 0]


@APP.route('/votea', methods=['GET', 'POST'])
def votea():
    SQL_CURSOR.execute("UPDATE votes SET a = a + 1 WHERE id = 1")
    SQL_CONNECTION.commit()
    TOTAL_VOTES[0] += 1
    return flask.render_template("voted_a.html")


@APP.route('/voteb', methods=['GET', 'POST'])
def voteb():
    SQL_CURSOR.execute("UPDATE votes SET b = b + 1 WHERE id = 1")
    SQL_CONNECTION.commit()
    TOTAL_VOTES[1] += 1
    return flask.render_template("voted_b.html")


@APP.route('/unvote_a', methods=['GET', 'POST'])
def unvote_a():
    TOTAL_VOTES[0] -= 1
    SQL_CURSOR.execute("UPDATE votes SET a = a - 1 WHERE id = 1")
    SQL_CONNECTION.commit()
    return flask.redirect(flask.url_for("index"))


@APP.route('/unvote_b', methods=['GET', 'POST'])
def unvote_b():
    TOTAL_VOTES[1] -= 1
    SQL_CURSOR.execute("UPDATE votes SET b = b - 1 WHERE id = 1")
    SQL_CONNECTION.commit()
    return flask.redirect(flask.url_for("index"))


@APP.route('/', methods=['GET', 'POST'])
def index():
    return flask.render_template("vote.html")


if __name__ == "__main__":
    APP.run(port=80, debug=DEBUG)
