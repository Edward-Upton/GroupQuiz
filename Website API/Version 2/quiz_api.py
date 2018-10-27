"""Charities Day Quiz Website Application

Authors:
    Ben Dodd (mitgobla)
    Edward Upton (engiego)
"""

import json
import os
import random
import time
import threading
import flask
from contextlib import closing
from flask import request  # , make_response
from flaskext.mysql import MySQL

DEBUG = True
APP = flask.Flask(__name__)
APP.config.from_object(__name__)

MYSQL = MySQL()
APP.config['MYSQL_DATABASE_USER'] = 'pyuser'
APP.config['MYSQL_DATABASE_PASSWORD'] = 'pyuser'
APP.config['MYSQL_DATABASE_DB'] = 'charities_day'
APP.config['MYSQL_DATABASE_HOST'] = 'localhost'
MYSQL.init_app(APP)

code_list = list()

CWD = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(CWD, "jsonQuiz.json"), "r") as fp:
    quizzesDict = json.load(fp)

with open(os.path.join(CWD, "jsonVote.json"), "r") as fp:
    votesDict = json.load(fp)


VOTING_READY = True  # Need API to toggle voting


def make_connection():
    """Used to make a connection to the database

    Returns:
        flaskext.mysql.connection -- Connection Object
    """

    return MYSQL.connect()


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


@APP.route('/getAdmin', methods=['GET', 'POST'])
def getAdmin():
    inputted_password = request.form['passwordField']
    if inputted_password != "test_password":  # Super secure password, btw
        return flask.redirect(flask.url_for('admin', passwordFailed=True))
    response = flask.make_response(flask.redirect(flask.url_for('adminPanel')))
    response.set_cookie('userAdmin', '1')
    return response


@APP.route('/adminPanel', methods=['GET', 'POST'])
def adminPanel():
    if not 'userAdmin' in request.cookies:
        return flask.redirect(flask.url_for('admin', notLoggedIn=True))

    with closing(make_connection()) as conn:
        with conn as cursor:
            # cursor = CONN.cursor()
            cursor.execute("SELECT COUNT(*) FROM `charities_day`.`users`")
            # CONN.commit()
            userCount = str(cursor.fetchone()[0])
        with conn as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM `charities_day`.`quiz-answers`")
            # CONN.commit()
            quizSqlLen = str(cursor.fetchone()[0])
        with conn as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM `charities_day`.`vote-results`")
            # CONN.commit()
            voteSqlLen = str(cursor.fetchone()[0])

    quizzes, votes = [], []
    for quiz in quizzesDict["quizzes"]:
        with closing(make_connection()) as conn:
            with conn as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM `charities_day`.`quiz-answers` WHERE `quizName` = '%s'" % quiz)
                # Get total answers for current quiz
                quizCount = cursor.fetchone()[0]

                quizQuestions = quizzesDict["quizzes"][quiz]["questions"]
                quizCorrectAnswers = quizzesDict["quizzes"][quiz]["answers"]
                quizResults = []
                for question in quizQuestions:
                    questionName = question[0]
                    questionAnswers = question[1:]
                    questionTally = []
                    for possibleAnswer in questionAnswers:
                        cursor.execute("SELECT COUNT(*) FROM `charities_day`.`quiz-answers` WHERE (`quizName` = '%s' AND `quizQuestion` = '%s' AND `questionAnswer` = '%s')" % (
                            quiz, quizQuestions.index(question), possibleAnswer))
                        questionTally.append(cursor.fetchone()[0])
                    quizResults.append(dict(
                        questionName=questionName,
                        questionAnswers=questionAnswers,
                        questionTally=questionTally,
                        correctAnswer=quizCorrectAnswers[quizQuestions.index(
                            question)]
                    ))

        quizzes.append(dict(
            quizName=quizzesDict["quizzes"][quiz]["name"],
            quizAvailable=quizzesDict["quizzes"][quiz]["available"],
            quizCount=quizCount,
            quizResults=quizResults
        ))

    for vote in votesDict["votes"]:
        with closing(make_connection()) as conn:
            with conn as cursor:
                cursor.execute("SELECT COUNT(*) FROM `charities_day`.`vote-results` WHERE `voteName` = '%s'" %
                               votesDict["votes"][vote]["name"])
                voteCount = cursor.fetchone()[0]

                voteResults = []
                voteTally = []
                voteQuestions = votesDict["votes"][vote]["options"]
                voteName = votesDict["votes"][vote]["name"]
                for possibleOption in voteQuestions:
                    cursor.execute(
                        "SELECT COUNT(*) FROM `charities_day`.`vote-results` WHERE (`voteName` = '%s' AND `voteAnswer` = '%s')" % (vote, possibleOption))
                    voteTally.append(cursor.fetchone()[0])
                voteResults.append(dict(
                    voteName=voteName,
                    voteQuestions=voteQuestions,
                    voteTally=voteTally,
                ))

        votes.append(dict(
            voteName=votesDict["votes"][vote]["name"],
            voteAvailable=votesDict["votes"][vote]["available"],
            voteResults=voteResults,
            voteCount=voteCount))

    return flask.render_template("adminPanel.html", userCount=userCount, quizSqlLen=quizSqlLen, voteSqlLen=voteSqlLen, quizzes=quizzes, votes=votes)


@APP.route('/normalUser', methods=['GET', 'POST'])
def normalUser():
    # global code_list
    if 'userCode' in request.cookies:
        # if request.cookies.get('userCode') in code_list:
        return flask.redirect(flask.url_for('home'))
        # else:
        #     code_list.append(request.cookies.get('userCode'))

    return flask.redirect(flask.url_for('getCode'))


def create_code():
    # global code_list
    with open(os.path.join(CWD, "names.txt")) as lfp:
        listNames = lfp.readlines()

    with open(os.path.join(CWD, "adjectives.txt")) as lfp:
        listAdjectives = lfp.readlines()

    code = listAdjectives[random.randint(0, len(listAdjectives)-1)].strip('\n').capitalize(
    ) + " " + listNames[random.randint(0, len(listAdjectives)-1)].strip('\n').capitalize()

    with closing(make_connection()) as conn:
        with conn as cursor:
            # cursor = CONN.cursor()
            cursor.execute(
                "SELECT COUNT(1) FROM `charities_day`.`users` WHERE `userCode` = '%s'" % (code))
        # CONN.commit()
        # code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            while code == cursor.fetchone()[0]:
                # code = ''.join(random.choices(
                #     string.ascii_uppercase + string.digits, k=4))
                code = listAdjectives[random.randint(0, len(listAdjectives)-1)].strip('\n').capitalize(
                ) + " " + listNames[random.randint(0, len(listAdjectives)-1)].strip('\n').capitalize()
                cursor.execute(
                    "SELECT COUNT(1) FROM `charities_day`.`users` WHERE `userCode` = '%s'" % (code))
                # CONN.commit()

        # code_list.append(code)

        with conn as cursor:
            cursor.execute("INSERT INTO `charities_day`.`users` (`userCode`) VALUES ('%s');" %
                           (code))
        # CONN.commit()
        # cursor.close()

    return code


@APP.route('/getCode', methods=['GET', 'POST'])
def getCode():
    if 'userCode' in request.cookies:
        response = flask.make_response(
            flask.redirect(flask.url_for('getYear')))
        # response.set_cookie('hasCode', "1")
        # response.set_cookie('userCode', request.cookies.get('userCode'))
    else:
        generated_code = create_code()
        # response = flask.make_response(flask.render_template("index.html", code=str(generated_code)))
        response = flask.make_response(
            flask.redirect(flask.url_for('getYear')))
        # response.set_cookie('hasCode', "1")
        response.set_cookie('userCode', generated_code)
    return response


@APP.route('/getYear', methods=['GET', 'POST'])
def getYear():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('home'))

    # return flask.render_template('yearForm.html', code=request.cookies.get('userCode'))
    return flask.render_template('yearForm.html')


@APP.route('/yearForm', methods=['GET', 'POST'])
def yearForm():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('home'))

    year = request.form['selectYear']

    response = flask.redirect(flask.url_for('home'))
    response.set_cookie('userGroup', year)
    userQuizData = {"quizzesAnswered": []}
    userVoteData = {"votesAnswered": []}
    response.set_cookie('userQuizData', str(json.dumps(userQuizData)))
    response.set_cookie('userVoteData', str(json.dumps(userVoteData)))
    return response


@APP.route('/home', methods=['GET', 'POST'])
def home():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    quizzes = list()
    votes = list()
    if isinstance(request.cookies.get("userQuizData"), str):
        userQuizData = json.loads(request.cookies.get("userQuizData"))
    else:
        userQuizData = {"quizzesAnswered": []}

    if isinstance(request.cookies.get("userVoteData"), str):
        userVoteData = json.loads(request.cookies.get("userVoteData"))
    else:
        userVoteData = {"votesAnswered": []}
    userQuizzesAnswered = userQuizData["quizzesAnswered"]
    userVotesAnswered = userVoteData["votesAnswered"]

    for quiz in quizzesDict["quizzes"]:
        if quizzesDict["quizzes"][quiz]["available"]:
            if not quiz in userQuizzesAnswered:
                quizzes.append(quizzesDict["quizzes"][quiz]["name"])

    for vote in votesDict["votes"]:
        if votesDict["votes"][vote]["available"]:
            if not vote in userVotesAnswered:
                votes.append(votesDict["votes"][vote]["name"])

    # if request.cookies.get("quizData"):

    return flask.render_template('home.html', code=request.cookies.get('userCode'),
                                 year=request.cookies.get("userGroup"), quizzes=quizzes, votes=votes, votesEntered=str(len(userVotesAnswered)), quizzesEntered=str(len(userQuizzesAnswered)))


@APP.route('/getVote', methods=['GET', 'POST'])
def getVote():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    vote = next(iter(request.form))  # Converts dict into iterable

    response = flask.make_response(flask.redirect(flask.url_for("votePage")))
    response.set_cookie('currentVote', vote)

    return response


@APP.route('/votePage', methods=['GET', 'POST'])
def votePage():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    currentVote = request.cookies.get('currentVote')

    global votesDict

    voteDict = votesDict["votes"][currentVote]

    if VOTING_READY:
        voteDescription = voteDict["description"]
        voteOptions = voteDict["options"]

        response = flask.make_response(flask.render_template("votePage.html",
                                                             code=request.cookies.get(
                                                                 "userCode"),
                                                             year=request.cookies.get(
                                                                 "userGroup"),
                                                             voteName=currentVote,
                                                             voteDescription=voteDescription,
                                                             voteOptions=voteOptions))
    else:
        response = flask.make_response(
            flask.redirect(flask.url_for("voteNotReady")))

    return response


@APP.route('/getVoteAnswer', methods=['GET', 'POST'])
def getVoteAnswer():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    userCode = request.cookies.get("userCode")
    userGroup = request.cookies.get("userGroup")
    currentVote = request.cookies.get("currentVote")

    answer = request.args.get("answer")
    if not answer:
        answer = "NaN"

    with closing(make_connection()) as conn:
        # cursor = CONN.cursor()
        with conn as cursor:
            cursor.execute("INSERT INTO `charities_day`.`vote-results` (`userCode`, `userGroup`, `voteName`, `voteAnswer`) VALUES ('%s', '%s', '%s', '%s');" %
                           (userCode, userGroup, currentVote, answer))
    # CONN.commit()

    response = flask.make_response(flask.render_template("voteFinished.html",
                                                         code=userCode,
                                                         year=userGroup,
                                                         vote_option=answer,
                                                         voteName=currentVote))
    voteData = json.loads(request.cookies.get("userVoteData"))
    voteData["votesAnswered"].append(currentVote)
    response.set_cookie("userVoteData", str(json.dumps(voteData)))
    return response


@APP.route('/getQuiz', methods=['GET', 'POST'])
def getQuiz():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    quiz = next(iter(request.form))

    response = flask.make_response(flask.redirect(flask.url_for('quizPage')))
    response.set_cookie('currentQuiz', quiz)
    response.set_cookie('questionNumber', '0')

    return response


@APP.route('/quizPage', methods=['GET', 'POST'])
def quizPage():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    currentQuiz = request.cookies.get('currentQuiz')
    questionNumber = int(request.cookies.get('questionNumber'))

    global quizzesDict

    quizDict = quizzesDict["quizzes"][currentQuiz]

    if questionNumber >= len(quizDict["questions"]):
        response = flask.make_response(flask.render_template("quizFinished.html",
                                                             code=request.cookies.get(
                                                                 "userCode"),
                                                             year=request.cookies.get(
                                                                 "userGroup"),
                                                             quizName=currentQuiz))

        quizData = json.loads(request.cookies.get("userQuizData"))

        quizData["quizzesAnswered"].append(currentQuiz)
        response.set_cookie("userQuizData", str(json.dumps(quizData)))

    elif questionNumber < len(quizDict["questions"]):
        questionList = quizDict["questions"][questionNumber]
        questionName = questionList[0]
        questionChoices = questionList[1:]

        response = flask.make_response(flask.render_template("quizPage.html", quizName=currentQuiz,
                                                             questionName=questionName, questionChoices=questionChoices,
                                                             code=request.cookies.get(
                                                                 "userCode"),
                                                             year=request.cookies.get("userGroup")))
        # response.set_cookie("questionNumber", str(questionNumber + 1))

    else:
        response = flask.make_response(flask.redirect(flask.url_for("/home")))

    return response


@APP.route('/getAnswer', methods=['GET', 'POST'])
def getAnswer():
    if not 'userCode' in request.cookies:
        return flask.redirect(flask.url_for('getCode'))

    if not 'userGroup' in request.cookies:
        return flask.redirect(flask.url_for('getYear'))

    userCode = request.cookies.get("userCode")
    userGroup = request.cookies.get("userGroup")
    currentQuiz = request.cookies.get("currentQuiz")
    questionNumber = request.cookies.get("questionNumber")

    global quizzesDict

    answer = request.args.get("answer")
    correctAnswer = quizzesDict["quizzes"][currentQuiz]["answers"][int(
        questionNumber)]
    if answer == correctAnswer:
        isCorrect = "y"
    else:
        isCorrect = "n"

    # cursor = CONN.cursor()
    with closing(make_connection()) as conn:
        with conn as cursor:
            cursor.execute("INSERT INTO `charities_day`.`quiz-answers` (`userCode`, `userGroup`, `quizName`, `quizQuestion`, `questionAnswer`, `isCorrect`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s');" %
                           (userCode, userGroup, currentQuiz, questionNumber, answer, isCorrect))
    # CONN.commit()

    response = flask.make_response(flask.redirect(flask.url_for("quizPage")))
    response.set_cookie("questionNumber", str(int(questionNumber) + 1))

    return response


@APP.route('/userGraphs', methods=['GET', 'POST'])
def userGraphs():

    votes = []

    for vote in votesDict["votes"]:
        with closing(make_connection()) as conn:
            with conn as cursor:
                cursor.execute("SELECT COUNT(*) FROM `charities_day`.`vote-results` WHERE `voteName` = '%s'" %
                               votesDict["votes"][vote]["name"])
                voteCount = cursor.fetchone()[0]

                voteResults = []
                voteTally = []
                voteQuestions = votesDict["votes"][vote]["options"]
                voteName = votesDict["votes"][vote]["name"]
                for possibleOption in voteQuestions:
                    cursor.execute(
                        "SELECT COUNT(*) FROM `charities_day`.`vote-results` WHERE (`voteName` = '%s' AND `voteAnswer` = '%s')" % (vote, possibleOption))
                    voteTally.append(cursor.fetchone()[0])
                voteResults = dict(
                    voteQuestions=voteQuestions,
                    voteTally=voteTally
                )

        votes.append(dict(
            voteName=votesDict["votes"][vote]["name"],
            voteAvailable=votesDict["votes"][vote]["available"],
            voteResults=voteResults,
            voteCount=voteCount))
    print(votes)
    return flask.render_template("userGraphs.html", votes=votes)


if __name__ == "__main__":
    # try:
    # thread = threading.Thread(target=updatingQuizVotes)
    # thread.start()
    APP.run(host="0.0.0.0", port=80, debug=DEBUG)
    # finally:
    #     return
