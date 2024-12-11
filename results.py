from app import app
from flask import render_template
from sqlalchemy import text
from db import db

@app.route("/result/<int:id>")
def result(id):
    sql = text("SELECT id, topic, exercise FROM exercises WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    exercises = result.fetchone()
    result2 = db.session.execute(text("SELECT id, answer, exercise_id FROM answers WHERE exercise_id=:id"), {"id": id})
    answers = result2.fetchall()
    result3 = db.session.execute(text("SELECT U.id, U.username, A.user_id from users U, answers A WHERE U.id = A.user_id"))
    users = result3.fetchone()
    return render_template("result.html", exercises=exercises, answers=answers, users=users)
