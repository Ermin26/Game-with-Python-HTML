import random
import time
import datetime
import json
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    make_response,
    flash,
)
from models import db, User
from uuid import uuid4


app = Flask(__name__)
app.secret_key = "game-key"
db.create_all()


@app.route("/", methods=["GET"])
def home():

    name = request.cookies.get("name")

    if name:

        user = db.query(User).filter_by(name=name).first()

    else:
        user = None

    return render_template("home.html", user=user)


@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    secret_number = random.randint(1, 30)

    games = 0

    wins = 0

    losses = 0

    pl_games = 0

    pl_wins = 0

    pl_losses = 0

    user = db.query(User).filter_by(name=name).first()

    if not user:

        user = User(
            name=name,
            email=email,
            password=password,
            secret_number=secret_number,
            games=games,
            wins=wins,
            losses=losses,
            pl_games=pl_games,
            pl_wins=pl_wins,
            pl_losses=pl_losses
        )

        db.add(user)
        db.commit()

    if password != user.password:
        Flash(f"Wrong password. Ty again")

    elif password == user.password:

        session_token = str(uuid4())

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("home")))
        response.set_cookie(
            "session_token", session_token, httponly=True, samesite="Strict"
        )
        response.set_cookie("name", name)

    return response

@app.route("/play", methods=["GET", "POST"])
def play():
    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()

    return render_template("playGame.html", user=user)\

@app.route("/scorers", methods=["GET", "POST"])
def score():
    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()

    return render_template("TopScores.html", user=user)

@app.route("/result", methods=["GET", "POST"])
def result():
    guess = int(request.form.get("guess"))

    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()

    if guess == user.secret_number:

        flash(f"Congralutions! You guessed it. The secret number was {guess}")

        user.pl_games += 1

        user.pl_wins += 1

        user.games += 1

        user.wins += 1

        new_secret = random.randint(1, 30)

        user.secret_number = new_secret

        db.add(user)
        db.commit()

        return render_template("success.html", user=user)

    elif guess > user.secret_number:

        flash(f"Wrong. Try a smaller one")

    elif guess < user.secret_number:

        flash(f"Wrong. Try a bigger one")

    else:
        user.losses += 1

        db.add(user)
        db.commit()

    return render_template("playGame.html", user=user)

@app.route("/giveup", methods=["GET", "POST"])
def give_up():
    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()

    user.losses += 1
    user.games += 1

    return render_template("home.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)
