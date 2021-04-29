import random
import time
import datetime
import json
import hashlib
import os
import requests
from sqla_wrapper import SQLAlchemy
import sqlalchemy
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    make_response,
    flash,

)
from models import db, User, Message
from uuid import uuid4


OWA = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)
app.secret_key = "game-secret-key"
db.create_all()



@app.route("/", methods=["GET"])
def home():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    if session_token:

        user = db.query(User).filter_by(session_token=session_token).first()

    else:
        user = None

    return render_template("home.html", user=user, location=location.title(), temperature=temperature, weather=weather)

@app.route("/please-register", methods=["GET", "POST"])
def reg():
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")

    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
    user = db.query(User).filter_by(name=name).first()

    if not user:
        flash(f"User doesn't exists. Please register.")
        return redirect(url_for('reg'))

    if hashed_pwd != user.password:
        flash(f"Wrong user name, email or password. Try again please.")
        return redirect(url_for("home"))

    else:
        session_token = str(uuid4())
        user.session_token = session_token
        user = User(online=True, offline=False)
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('home')))
        response.set_cookie('session_token', session_token)

        return response

@app.route("/register", methods=["POST"])
def register():
    location = request.args.get("location", "Maribor")

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

    secret_number = random.randint(1, 30)

    games = 0

    wins = 0

    losses = 0

    score = 0

    user = db.query(User).filter_by(name=name).first()

    if name and email and password:

        if not user:

            user = User(
                name=name,
                email=email,
                password=hashed_pwd,
                secret_number=secret_number,
                games=games,
                wins=wins,
                losses=losses,
                score=score,
                online=True,
                offline=False,
                location=location)

            session_token = str(uuid4())
            user.session_token = session_token

            db.add(user)
            db.commit()

            response = make_response(redirect(url_for("home")))
            response.set_cookie("session_token", session_token,)

        return response
    else:
        flash(f"Please fill all data to complete registration")
        return render_template("register.html", user=user)


@app.route("/play", methods=["GET", "POST"])
def play():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    return render_template("playGame.html", user=user, location=location.title(), temperature=temperature, weather=weather)


@app.route("/scorers", methods=["GET", "POST"])
def score():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    users = db.query(User).order_by(User.score.desc()).all()

    return render_template("TopScores.html", user=user, users=users,  location=location.title(), temperature=temperature, weather=weather)


@app.route("/result", methods=["GET", "POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:

        flash(f"Congralutions! You guessed it. The secret number was {guess}")

        user.games += 1

        user.wins += 1

        user.score += 2

        new_secret = random.randint(1, 30)

        user.secret_number = new_secret

        db.add(user)
        db.commit()

        location = request.args.get("location", "Maribor")
        r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")
        tempwat = r.json()
        temperature = tempwat["main"]["temp"]
        weather = tempwat["weather"][0]["main"]

        return render_template("success.html", user=user, location=location.title(), temperature=temperature, weather=weather)

    elif guess > user.secret_number:

        flash(f"Wrong. Try a smaller one")

    elif guess < user.secret_number:

        flash(f"Wrong. Try a bigger one")

    else:
        user.games += 1
        user.losses += 1
        user.score -= 1
        db.add(user)
        db.commit()

    return render_template("playGame.html", user=user)


@app.route("/giveup", methods=["GET", "POST"])
def give_up():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    user.games += 1
    user.losses += 1
    user.score -= 1

    db.add(user)
    db.commit()

    location = request.args.get("location", "Maribor")
    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")
    tempwat = r.json()
    temperature = tempwat["main"]["temp"]
    weather = tempwat["weather"][0]["main"]

    return render_template("home.html", user=user, location=location.title(), temperature=temperature, weather=weather)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    name = request.form.get("name")

    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user, name=name, location=location.title(), temperature=temperature, weather=weather)

    else:

        return render_template("home.html", location=location.title(), temperature=temperature, weather=weather)


@app.route("/profile/edit", methods=["GET", "POST"])
def edit():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if not user:
        return redirect(url_for('home'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("pasword")

        if name:
            user.name = name

        if email:
            user.email = email

        if password:
            hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
            user.password = hashed_pwd

        db.add(user)
        db.commit()

        return redirect(url_for('profile'))

    return render_template("edit.html", user=user, location=location.title(), temperature=temperature, weather=weather)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if not user:
        return render_template("home.html", user=user, location=location.title(), temperature=temperature, weather=weather)

    if request.method == "POST":
        if user:
            db.delete(user)
            db.commit()

        response = make_response(redirect(url_for('home')))
        response.set_cookie("session_token", "")

        return response

    return render_template("profile.html", user=user, location=location.title(), temperature=temperature, weather=weather)


@app.route("/messages", methods=["GET", "POST"])
def mes():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()
    messages = db.query(Message).filter_by(reciver_id=user.id).all()

    if user:
        return render_template("messages.html", user=user, messages=messages, location=location.title(), temperature=temperature, weather=weather)

    else:
        "Please sign in or login if you want to go on that page."
        return render_template("home.html", user=user, messages=messages, location=location.title(), temperature=temperature, weather=weather)


@app.route("/received", methods=["GET", "POST"])
def received():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()
    messages = db.query(Message).filter_by(reciver_id=user.id).all()

    if user:
        return render_template("received.html", user=user, messages=messages, location=location.title(), temperature=temperature, weather=weather)

    else:
        "Please sign in or login if you want to go on that page."
        return render_template("home.html", user=user, messages=messages, location=location.title(), temperature=temperature, weather=weather)


@app.route("/allusers", methods=["GET", "POST"])
def allusers():
    location = request.args.get("location", "Maribor")

    r = requests.get(f"{OWA}?q={location}&units=metric&appid={API_KEY}")

    tempwat = r.json()
    temperature = tempwat["main"]["temp"]

    weather = tempwat["weather"][0]["main"]

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()
    users = db.query(User).all()

    if user:
        return render_template("users.html", user=user, users=users, location=location.title(), temperature=temperature, weather=weather)

    else:
        "Please sign in or login if you want to go on that page."
        return render_template("home.html", user=user, messages=messages, location=location.title(), temperature=temperature, weather=weather)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:

        user.session_token = ""
        user.online = False
        user.offline = True

        db.add(user)
        db.commit()

    response = make_response(redirect(url_for('home')))
    response.set_cookie("session_token", "")

    return response


if __name__ == "__main__":
    app.run(debug=True)
