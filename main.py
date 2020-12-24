import random
import time
import datetime
from flask import Flask, request, render_template, redirect, url_for, make_response, flash
from models import db, User
from uuid import uuid4


app = Flask(__name__)
app.secret_key = "game-key"
db.create_all()


# preveri če obstaja korisnik

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

    user = db.query(User).filter_by(name=name).first()

    if not user:

        user = User(name=name, email=email, password=password, secret_number=secret_number, games=games, wins=wins, losses=losses)

        db.add(user)
        db.commit()

    if password != user.password:
        Flash(f"Wrong password. Ty again")

    elif password == user.password:

        session_token = str(uuid4())

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('home')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')
        response.set_cookie("name", name)

    return response

@app.route("/play", methods=["GET", "POST"])
def play():
    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()

    return render_template("playGame.html", user=user)

@app.route("/result", methods=["GET", "POST"])
def result():
    guess = int(request.form.get("guess"))

    name = request.cookies.get("name")

    user = db.query(User).filter_by(name=name).first()



    if guess == user.secret_number:

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


if __name__ == "__main__":
    app.run(debug=True)


