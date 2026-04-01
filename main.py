from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///school.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    age = db.Column(db.Integer)
    level = db.Column(db.String(10))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    text = db.Column(db.String(300))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Completion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    date = db.Column(db.String(20))


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    certified_ids = db.session.query(Completion.student_id).all()
    certified_ids = [c[0] for c in certified_ids if c[0] is not None]

    students = Student.query.filter(~Student.id.in_(certified_ids)).count()
    certifications = len(certified_ids)

    reviews = Review.query.all()
    review_count = len(reviews)

    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render_template(
        "index.html",
        students=students,
        certifications=certifications,
        review_count=review_count,
        avg_rating=avg_rating
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        student = Student(
            name=request.form.get("name"),
            surname=request.form.get("surname"),
            age=request.form.get("age"),
            level=request.form.get("level")
        )
        db.session.add(student)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/complete", methods=["GET", "POST"])
def complete():
    if request.method == "POST":
        student_id = request.form.get("student_id")
        date = request.form.get("date")

        if student_id:
            completion = Completion(
                student_id=student_id,
                date=date
            )
            db.session.add(completion)
            db.session.commit()

        return redirect("/")

    students = Student.query.all()
    return render_template("complete.html", students=students)


@app.route("/review", methods=["GET", "POST"])
def review():
    if request.method == "POST":
        name = request.form.get("name")
        rating = int(request.form.get("rating"))
        text = request.form.get("text")

        if name and rating:
            db.session.add(Review(name=name, rating=rating, text=text))
            db.session.commit()

        return redirect("/")

    return render_template("review.html")


if __name__ == "__main__":
    app.run(debug=True)
