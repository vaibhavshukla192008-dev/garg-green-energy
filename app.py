from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)

app.secret_key = "garg-green-energy-local-key"

DATABASE = "garg_green_energy.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            location TEXT,
            requirement TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'New',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/projects")
def projects():
    return render_template("projects.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        location = request.form.get("location", "").strip()
        requirement = request.form.get("requirement", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not phone or not requirement:
            flash("Please fill all required fields.", "error")
            return redirect(url_for("contact"))

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO enquiries
            (name, phone, email, location, requirement, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            location,
            requirement,
            message
        ))

        connection.commit()
        connection.close()

        flash(
            "Your enquiry has been submitted successfully.",
            "success"
        )

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)