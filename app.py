import json
import os
import sqlite3
# from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, custom_date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["date"] = custom_date

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
sqliteConnection = sqlite3.connect("./finance.db", check_same_thread=False)
sqliteConnection.row_factory = sqlite3.Row
db = sqliteConnection.cursor()

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    load_board = {"loads":[]}
    if len(request.args) > 1:
        rows = db.execute(
            "SELECT * FROM load_board JOIN companies on load_board.carrier_id = companies.id "
            "where lot_id like ? AND "
            "origin like ? AND "
            "destination like ? ;"
            , [
                '%' + str(request.args.get("lot_id")) + '%'
                , '%' + str(request.args.get("origin")) + '%'
                , '%' + str(request.args.get("destination")) + '%'
               ]
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM load_board JOIN companies on load_board.carrier_id = companies.id ;").fetchall()
    for i in range(len(rows)):
        load_board["loads"].append(dict(rows[i]))
        load_board["loads"][i]["contact"] = {"tel": load_board["loads"][i]["tel"],
                                             "email": load_board["loads"][i]["email"]}
    print(load_board)
    return render_template("index.html", loads=load_board)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol").upper():
            return apology("must provide symbol", 400)
        quoted = lookup(request.form.get("symbol").upper())
        if not request.form.get("shares"):
            return apology("must provide shares number", 400)
        if lookup(request.form.get("symbol").upper()) is None:
            return apology("incorrect symbol", 400)
        quoted = lookup(request.form.get("symbol").upper())
        budget = db.execute("SELECT cash FROM users WHERE id = ?", [session["user_id"]])
        if not request.form.get("shares").isnumeric():
            return apology("shares can not be fractional, negative or and non-numericl", 400)
        if not float(request.form.get("shares")) > 0 or float(request.form.get("shares")) % 10 == 0:
            return apology("shares can not be fractional, negative or and non-numericl", 400)
        if float(request.form.get("shares")) * quoted["price"] <= budget[0]["cash"]:
            db.execute("INSERT INTO transactions (users_id, symbol, name, shares, price) VALUES (?, ?, ?, ?, ?)",
                       [session["user_id"], request.form.get(
                           "symbol").upper(), quoted["name"], float(request.form.get("shares")), quoted["price"]])
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       budget[0]["cash"] - (float(request.form.get("shares")) * quoted["price"]), session["user_id"])
        else:
            return apology("not enough funds", 400)

        # return redirect("/")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    """Buy shares of stock"""
    if request.method == "POST":
        # Ensure symbol was submitted
        if not request.form.get("amount"):
            return apology("must provide amount", 400)
        if not request.form.get("amount").isnumeric():
            return apology("amount can not be non-numericl", 400)
        if not float(request.form.get("amount")) > 0:
            return apology("amount can not be negative", 400)
        budget = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   budget[0]["cash"] + float(request.form.get("amount")), session["user_id"])
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("addcash.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM transactions WHERE users_id = ? order by timestamp DESC", session["user_id"])
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute('SELECT * FROM users WHERE username = ?;', [request.form.get("username").lower()]).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    if request.method == "POST":
        if not request.form.get("currentPassword"):
            return apology("must provide current username", 400)

        elif not request.form.get("newPassword"):
            return apology("must provide new password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide new password confirmation", 400)
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(user[0]["hash"], request.form.get("currentPassword")):
            return apology("invalid current password", 400)
        elif not request.form.get("newPassword") == request.form.get("confirmation"):
            return apology("password confirmation does not match", 400)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(
            request.form.get("newPassword"), "sha512", 8), session["user_id"])
        return redirect("/")
    else:
        return render_template("changepassword.html")


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("profile.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol").upper():
            return apology("must provide symbol", 400)
        if lookup(request.form.get("symbol").upper()) is None:
            return apology("incorrect symbol", 400)
        quoted = lookup(request.form.get("symbol").upper())
        # return redirect("/quoted")

        return render_template("quoted.html", name=quoted['name'], symbol=quoted['symbol'].upper(),
                               price=quoted['price'])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("password and confirmation does not match", 400)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").lower())

        # Ensure username exists and password is correct
        if len(rows):
            return apology("username is not available", 400)
        password_hash = generate_password_hash(request.form.get("password"), "sha512", 8)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username").lower(),
                   password_hash)
        return render_template("success.html")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    portfolio = db.execute(
        "SELECT symbol, name, sum(shares) as shares FROM transactions WHERE users_id = ? group by symbol",
        session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    availableSymbols = []
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol").upper():
            return apology("must provide symbol", 400)
        for symbol in portfolio:
            availableSymbols.append(symbol["symbol"])
        if request.form.get("symbol").upper() not in availableSymbols:
            return apology("incorrect symbol", 400)
        if not request.form.get("shares"):
            return apology("must provide number of shares", 400)
        stock = next((item for item in portfolio if item['symbol'] == request.form.get("symbol").upper()), None)
        if stock["shares"] - float(request.form.get("shares")) < 0:
            return apology("don't have enough shares", 400)
        quoted = lookup(request.form.get("symbol").upper())
        db.execute("INSERT INTO transactions (users_id, symbol, name, shares, price) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], request.form.get(
                "symbol").upper(), quoted["name"], float(request.form.get("shares")) * -1, quoted["price"])
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]["cash"] +
                   quoted["price"] * float(request.form.get("shares")), session["user_id"])

        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("sell.html", symbols=portfolio)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)