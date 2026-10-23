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
# Drop the old table if it exists (fixes the missing column error) and create the new one
db.execute("DROP TABLE IF EXISTS herring")

db.execute("""
    CREATE TABLE herring (
        count_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dam_id INTEGER,
        year INTEGER,
        sd INTEGER,
        population INTEGER,
        ninty_above INTEGER,
        ninty_below INTEGER,
        FOREIGN KEY (dam_id) REFERENCES dams(dam_id)
    )
""")

# Seed your data
herring_data = [
    (2, 2017, 574, 1523, 2097, 949),
    (2, 2018, 413, 1787, 2200, 1374),
    (2, 2019, 232, 475, 707, 243),
    (2, 2020, 652, 927, 1579, 275),
    (2, 2021, 1454, 2734, 4188, 1280),
    (2, 2022, 269, 776, 1045, 507),
    (2, 2023, 708, 2585, 3293, 1877),
    (2, 2024, 396, 1042, 1438, 646),
    (2, 2025, 330, 429, 759, 99),
    (2, 2026, 1135, 2471, 3606, 1336),
    (2, 2016, 0, 0, 0, 0)
]

for row in herring_data:
    db.execute(
        "INSERT INTO herring (dam_id, year, sd, population, ninty_above, ninty_below) VALUES (?, ?, ?, ?, ?, ?)",
        row[0], row[1], row[2], row[3], row[4], row[5]
    )
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

@app.route("/data")
def data():
    data = db.execute("SELECT year, population, ninty_above, ninty_below FROM herring ORDER BY year ASC")
    year = []
    population = []
    ninty_above = []
    ninty_below = []
    for row in data:
        year.append(row["year"])
        population.append(row["population"])
        ninty_above.append(row["ninty_above"])
        ninty_below.append(row["ninty_below"])
    return render_template("data.html", year=year, population=population, ninty_above=ninty_above, ninty_below=ninty_below)
