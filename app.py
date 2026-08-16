import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
"""Imported this to make sure that the user doesn't import any bad words. Used Gemini to help me with the logic (what to import that has a list of bad words) and make sure that all of the comments are filtered."""
from better_profanity import profanity
profanity.load_censor_words()

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///andover.db")
db1 = SQL("sqlite:///comments.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

areasToExplore = [False, False, False, False, False]

# Code for the website starts here:
@app.route("/")
def startUp():
    areasToExplore[0] = True
    return render_template("index.html", areas=areasToExplore)

@app.route("/overview")
def overViewPage():
    areasToExplore[1] = True
    return render_template("overview.html")

@app.route("/marland")
def marLand():
    areasToExplore[2] = True
    return render_template("marland.html")

@app.route("/balmoral")
def balmoral():
    areasToExplore[3] = True
    return render_template("balmoral.html")

@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        name = request.form.get("Name")
        """This statement is used to make sure the user didn't write any bad words. Gemini helped me with this statement."""
        if profanity.contains_profanity(name):
            return redirect("/comments")
        if not name:
            name = "Anonymous"
        text = request.form.get("Comment")
        """This statement is used to make sure the user didn't write any bad words. Gemini helped me with this statement."""
        if not text or profanity.contains_profanity(text):
            return redirect("/comments")
        db1.execute("INSERT INTO comments (name, statement) VALUES (?, ?)", name, text)
        return redirect("/comments")
    else:
        statementsFromUser = db1.execute("SELECT * FROM comments")
        areasToExplore[4] = True
        return render_template("comments.html", statementsFromUser=statementsFromUser)
