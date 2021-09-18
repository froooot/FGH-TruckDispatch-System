import arrow
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

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    load_board = {"loads": []}
    maxepoch = 32525679833000
    maxdh = 30000
    if len(request.args) > 1:
        db = sqliteConnection.cursor()
        rows = db.execute(
            "SELECT * FROM load_board JOIN companies on load_board.carrier_id = companies.id "
            "join truck_type on truck_type.id = load_board.truck_type_id where "
            "lot_id like ? AND "
            "pickup <= ? AND "
            "delivery <= ? AND "
            "origin like ? AND "
            "dh_o <= ? AND "
            "destination like ? AND "
            "dh_d <= ? AND "
            "(tel like ? OR email like ?) AND "
            "weight <= ? AND "
            "rate <= ?;"
            , [
                '%' + ("" if str(request.args.get("lot_id")) == "NaN" else str(request.args.get("lot_id"))) + '%'
                , maxepoch if request.args.get("pickup") == "NaN" else int(request.args.get("pickup")) * 1000
                , maxepoch if request.args.get("delivery") == "NaN" else int(request.args.get("delivery")) * 1000
                , '%' + ("" if str(request.args.get("origin")) == "NaN" else str(request.args.get("origin"))) + '%'
                , maxdh if request.args.get("dh-o") == "NaN" else request.args.get("dh-o")
                , '%' + ("" if str(request.args.get("destination")) == "NaN" else str(
                    request.args.get("destination"))) + '%'
                , maxdh if request.args.get("dh-d") == "NaN" else request.args.get("dh-d")
                , '%' + ("" if str(request.args.get("contact")) == "NaN" else str(request.args.get("contact"))) + '%'
                , '%' + ("" if str(request.args.get("contact")) == "NaN" else str(request.args.get("contact"))) + '%'
                , maxdh if request.args.get("weight") == "NaN" else request.args.get("weight")
                , maxdh if request.args.get("rate") == "NaN" else request.args.get("rate")
            ]
        ).fetchall()
        db.close()
    else:
        db = sqliteConnection.cursor()
        rows = db.execute(
            "SELECT * FROM load_board JOIN companies on load_board.carrier_id = companies.id "
            "join truck_type on truck_type.id = load_board.truck_type_id;").fetchall()
        db.close()
    for i in range(len(rows)):
        load_board["loads"].append(dict(rows[i]))
        load_board["loads"][i]["contact"] = {"tel": load_board["loads"][i]["tel"],
                                             "email": load_board["loads"][i]["email"]}
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
        db = sqliteConnection.cursor()
        rows = db.execute('SELECT * FROM users WHERE username = ?;', [request.form.get("username").lower()]).fetchall()
        db.close()

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
        db = sqliteConnection.cursor()
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"]).fetchone()
        db.close()
        if not check_password_hash(user[0]["hash"], request.form.get("currentPassword")):
            return apology("invalid current password", 400)
        elif not request.form.get("newPassword") == request.form.get("confirmation"):
            return apology("password confirmation does not match", 400)
        db = sqliteConnection.cursor()
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(
            request.form.get("newPassword"), "sha512", 8), session["user_id"])
        db.close()
        return redirect("/")
    else:
        db = sqliteConnection.cursor()
        user = dict(db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]]).fetchone())
        db.close()
        # user["photo"] = user["photo"].decode('utf-8-sig')
        return render_template("changepassword.html", user=user)


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    db = sqliteConnection.cursor()
    row = db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]]).fetchone()
    user = dict(row)
    db.close()
    return render_template("profile.html", user=user)


@app.route("/profileedit", methods=["GET", "POST"])
@login_required
def profileedit():
    if request.method == "POST":
        db = sqliteConnection.cursor()
        db.execute("UPDATE users SET "
                   "firstname = ?"
                   ", lastname = ?"
                   ", email = ?"
                   ", phone = ?"
                   ", bio = ?"
                   ", photo = ?"
                   "  WHERE id = ?", [
                       request.form.get("firstname")
                       , request.form.get("lastname")
                       , request.form.get("email")
                       , request.form.get("phone")
                       , request.form.get("bio")
                       , request.form.get("photo")
                       , session["user_id"]
                   ])
        sqliteConnection.commit()
        db.close()

        return redirect("/profile")
    else:
        db = sqliteConnection.cursor()
        row = db.execute("SELECT * FROM users WHERE id = ?", [session["user_id"]]).fetchone()
        user = dict(row)
        # user["photo"] = user["photo"].decode('utf-8-sig')
        db.close()
        return render_template("profileedit.html", user=user)


@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Add new load to the board"""
    if request.method == "POST":
        pickup = int(float(arrow.get(request.form.get("pickup")).format('X')) * 1000)
        delivery = int(float(arrow.get(request.form.get("delivery")).format('X')) * 1000)
        db = sqliteConnection.cursor()
        db.execute("INSERT INTO load_board ("
                   "lot_id"
                   ", truck_type_id"
                   ", origin"
                   ", dh_o"
                   ", destination"
                   ", dh_d"
                   ", broker_id"
                   ", carrier_id"
                   ", weight"
                   ", rate "
                   ", pickup"
                   ", delivery"
                   ", users_id"
                   ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
                   ,[
                   request.form.get("lotid")
                   , request.form.get("type")
                   , request.form.get("origin")
                   , request.form.get("dho")
                   , request.form.get("destination")
                   , request.form.get("dhd")
                   , request.form.get("broker")
                   , request.form.get("carrier")
                   , request.form.get("weight")
                   , request.form.get("rate")
                   , pickup
                   , delivery
                   , session["user_id"]
                   ])
        sqliteConnection.commit()
        db.close()
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        data = {}
        db = sqliteConnection.cursor()
        rows = db.execute("SELECT * FROM truck_type;").fetchall()
        db.close()
        data["types"] = rows
        db = sqliteConnection.cursor()
        rows = db.execute("SELECT * FROM companies where type = 1;").fetchall()
        db.close()
        data["brokers"] = rows
        db = sqliteConnection.cursor()
        rows = db.execute("SELECT * FROM companies where type = 2;").fetchall()
        db.close()
        data["carriers"] = rows
        return render_template("new.html", data=data, key=os.environ.get("google_API_KEY"))


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
        db = sqliteConnection.cursor()
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").lower())
        db.close()
        # Ensure username exists and password is correct
        if len(rows):
            return apology("username is not available", 400)
        password_hash = generate_password_hash(request.form.get("password"), "sha512", 8)
        db = sqliteConnection.cursor()
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username").lower(),
                   password_hash)
        db.close()
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
        sqliteConnection.commit()
        db.close()
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
