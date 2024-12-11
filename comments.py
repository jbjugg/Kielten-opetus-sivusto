from app import app
from flask import render_template, request, redirect, session
from sqlalchemy import text
from db import db

@app.route("/create_comment", methods=["POST"])
def create_comment():
    comment = request.form.get("comment")
    exercise_id = request.form.get("exercise_id")
    answer_id = request.form.get("answer_id")
    user_id = session.get("user_id")
    sql = text("INSERT INTO comments (comment, exercise_id, answer_id, user_id) VALUES (:comment, :exercise_id, :answer_id, :user_id) RETURNING id")
    db.session.execute(sql, {"comment": comment, "exercise_id": exercise_id, "answer_id": answer_id, "user_id": user_id})
    db.session.commit()
    return redirect("/")

@app.route("/comment/<int:id>")
def comment(id):
    result = db.session.execute(text("SELECT id, answer FROM answers WHERE id=:id"), {"id":id})
    answers = result.fetchone()
    result2 = db.session.execute(text("SELECT id, exercise_id, answer_id, comment FROM comments WHERE answer_id=:id"), {"id": id})
    comments = result2.fetchall()
    result3 = db.session.execute(text("SELECT U.id, U.username, C.user_id from users U, comments C WHERE U.id = C.user_id"))
    users = result3.fetchone()
    return render_template("comment.html", answers=answers, comments=comments, users=users)
