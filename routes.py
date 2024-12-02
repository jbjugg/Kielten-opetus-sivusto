from app import app
from flask import render_template, request, redirect, session
from db import db
from sqlalchemy import text
import users




@app.route("/", methods=["GET"])
def front():

    sql = text("""
        SELECT languages.id, languages.language, COUNT(exercises.id) AS exercise_count
        FROM languages
        LEFT JOIN exercises ON languages.id = exercises.language_id
        GROUP BY languages.id
        ORDER BY languages.language
    """)
    result = db.session.execute(sql)
    languages = result.fetchall()
    return render_template("front.html", languages=languages)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        if users.register(username, password1):
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")


    

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/new_language", methods=["POST"])
def new_language():
    language = request.form["language"]
    sql = text("INSERT INTO languages (language) VALUES (:language) RETURNING id")
    db.session.execute(sql, {"language":language})
    db.session.commit()
    return redirect("/")


@app.route("/language/<int:id>")
def language(id):
    result = db.session.execute(text("SELECT language FROM languages WHERE id=:id"), {"id":id})
    language = result.fetchone()[0]
    result2 = db.session.execute(text("SELECT id, topic, deadline FROM exercises WHERE language_id=:id"), {"id":id})
    exercises = result2.fetchall()
    result3 = db.session.execute(text("SELECT COUNT(exercise) FROM exercises WHERE language_id=:id"), {"id":id})
    counter = result3.fetchone()[0]
    result4 = db.session.execute(text("SELECT id FROM answers"))
    answer = result4.fetchall()
    
    return render_template("language.html", id=id, language=language, exercises=exercises, counter=counter, answer=answer)


@app.route("/new")
def new():
    result = db.session.execute(text("SELECT L.id, L.language, U.id AS user_id FROM languages L, users U ORDER BY language"))
    languages = result.fetchall()
    return render_template("new.html", languages=languages)

@app.route("/create", methods=["POST"])
def create():
    topic = request.form.get("topic")
    exercise = request.form.get("exercise")
    deadline = request.form.get("deadline")
    language_id = request.form.get("language_id")
    user_id = request.form.get("user_id")
    if not topic:
        return "Topic cannot be empty", 400
    try:
        sql = text("INSERT INTO exercises (topic, exercise, deadline, language_id) VALUES (:topic, :exercise, :deadline, :language_id) RETURNING id")  
        db.session.execute(sql, {"topic": topic, "exercise" :exercise, "deadline" :deadline, "language_id" :language_id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error creating exercise:", e)
        return "An error occurred while creating the exercise.", 500
    return redirect("/")

@app.route("/exercise/<int:id>")
def exercise(id):  
    result = db.session.execute(text("SELECT id, topic, exercise FROM exercises WHERE id=:id") , {"id": id})
    exercises = result.fetchone()
    return render_template("exercise.html", exercises=exercises)

@app.route("/answer", methods=["POST"])
def answer():
    answer = request.form.get("answer")
    exercise_id = request.form.get("id")
    sql = text("INSERT INTO answers (answer, exercise_id) VALUES (:answer, :exercise_id) RETURNING id")
    db.session.execute(sql, {"answer": answer, "exercise_id": exercise_id})
    db.session.commit()
    return redirect("/")

@app.route("/result/<int:id>")
def result(id):
    sql = text("SELECT id, topic, exercise FROM exercises WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    exercises = result.fetchone()
    result2 = db.session.execute(text("SELECT id, answer, exercise_id FROM answers WHERE exercise_id=:id"), {"id": id})
    answers = result2.fetchall()
    return render_template("result.html", exercises=exercises, answers=answers)

@app.route("/create_comment", methods=["POST"])
def create_comment():
    comment = request.form.get("comment")
    exercise_id = request.form.get("exercise_id")
    answer_id = request.form.get("answer_id")
    sql = text("INSERT INTO comments (comment, exercise_id, answer_id) VALUES (:comment, :exercise_id, :answer_id) RETURNING id")
    db.session.execute(sql, {"comment": comment, "exercise_id": exercise_id, "answer_id": answer_id})
    db.session.commit()
    return redirect("/")

@app.route("/comment/<int:id>")
def comment(id):
    result = db.session.execute(text("SELECT id, answer FROM answers WHERE id=:id"), {"id":id})
    answers = result.fetchone()
    result2 = db.session.execute(text("SELECT id, exercise_id, answer_id, comment FROM comments WHERE answer_id=:id"), {"id": id})
    comments = result2.fetchall()
    return render_template("comment.html", answers=answers, comments=comments)