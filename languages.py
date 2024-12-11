from app import app
from flask import render_template, redirect, request
from sqlalchemy import text
from db import db

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
    result5 = db.session.execute(text("SELECT U.id, U.username, E.user_id from users U, exercises E WHERE U.id = E.user_id"))
    users = result5.fetchone()
    answer = result4.fetchall()
    
    return render_template("language.html", id=id, language=language, exercises=exercises, counter=counter, answer=answer, users=users)
