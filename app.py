import os
import sqlite3

from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session


# ==================================================
# APPLICATION
# ==================================================

app = Flask(__name__)

# Production mein Render environment variable use karega.
# Local mein fallback value use hogi.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "garg-green-energy-local-development-key"
)


# ==================================================
# CONFIGURATION
# ==================================================

DATABASE = os.environ.get(
    "DATABASE_PATH",
    "garg_green_energy.db"
)

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "change-this-password"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

def init_db():

    connection = get_db_connection()

    # ----------------------------------------------
    # ENQUIRIES
    # ----------------------------------------------

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

    # ----------------------------------------------
    # REVIEWS
    # ----------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ----------------------------------------------
    # WEBSITE CONTENT
    # ----------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS website_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            tagline TEXT,
            established TEXT,
            description TEXT,
            head_office TEXT,
            other_location TEXT,

            about_label TEXT,
            about_heading TEXT,
            about_description_1 TEXT,
            about_description_2 TEXT,

            focus_title TEXT,
            focus_description TEXT,

            solutions_title TEXT,
            solutions_description TEXT,

            service_title TEXT,
            service_description TEXT,

            location_heading TEXT,
            location_description TEXT,

            cta_label TEXT,
            cta_heading TEXT,
            cta_description TEXT,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ==================================================
    # DATABASE MIGRATION
    # ==================================================

    existing_columns = connection.execute("""
        PRAGMA table_info(website_content)
    """).fetchall()

    existing_column_names = {
        column["name"]
        for column in existing_columns
    }

    new_columns = {

        "about_label": "TEXT",
        "about_heading": "TEXT",
        "about_description_1": "TEXT",
        "about_description_2": "TEXT",

        "focus_title": "TEXT",
        "focus_description": "TEXT",

        "solutions_title": "TEXT",
        "solutions_description": "TEXT",

        "service_title": "TEXT",
        "service_description": "TEXT",

        "location_heading": "TEXT",
        "location_description": "TEXT",

        "cta_label": "TEXT",
        "cta_heading": "TEXT",
        "cta_description": "TEXT"
    }

    for column_name, column_type in new_columns.items():

        if column_name not in existing_column_names:

            connection.execute(
                f"""
                ALTER TABLE website_content
                ADD COLUMN {column_name} {column_type}
                """
            )

    # ==================================================
    # DEFAULT WEBSITE CONTENT
    # ==================================================

    existing_content = connection.execute("""
        SELECT *
        FROM website_content
        ORDER BY id ASC
        LIMIT 1
    """).fetchone()

    if existing_content is None:

        connection.execute("""
            INSERT INTO website_content
            (
                company_name,
                tagline,
                established,
                description,
                head_office,
                other_location,

                about_label,
                about_heading,
                about_description_1,
                about_description_2,

                focus_title,
                focus_description,

                solutions_title,
                solutions_description,

                service_title,
                service_description,

                location_heading,
                location_description,

                cta_label,
                cta_heading,
                cta_description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            "GARG GREEN ENERGY",

            "POWERING A GREENER TOMORROW",

            "2025",

            "Complete solar energy solutions for homes, businesses, industries, institutions, agriculture and government projects.",

            "01 First Floor, SK Building, Near DK Chauraha, Sanatan Nagar, Lucknow – 226068",

            "Sehda Mahrajpur, Azamgarh",

            "WHO WE ARE",

            "Growing with Clean Energy",

            "Complete solar energy solutions for homes, businesses, industries, institutions, agriculture and government projects.",

            "GARG GREEN ENERGY is focused on providing reliable renewable-energy solutions and supporting customers with solar-related products, electrical components, installation, commissioning and service support.",

            "Our Focus",

            "Solar and renewable-energy solutions for homes, shops, offices, factories, institutions, farmers and government project requirements.",

            "Our Solutions",

            "Electrical components, installation solutions, commissioning and service support for solar-related requirements.",

            "Service Support",

            "We provide installation, commissioning and ongoing service support according to customer requirements.",

            "Where We Are",

            "Our head office is located in Lucknow, Uttar Pradesh.",

            "LET'S WORK TOGETHER",

            "Looking for a Reliable Energy Solution?",

            "Get in touch with GARG GREEN ENERGY for your solar and renewable-energy requirements."

        ))

    else:

        defaults = {

            "about_label": "WHO WE ARE",

            "about_heading": "Growing with Clean Energy",

            "about_description_1":
                "Complete solar energy solutions for homes, businesses, industries, institutions, agriculture and government projects.",

            "about_description_2":
                "GARG GREEN ENERGY is focused on providing reliable renewable-energy solutions and supporting customers with solar-related products, electrical components, installation, commissioning and service support.",

            "focus_title": "Our Focus",

            "focus_description":
                "Solar and renewable-energy solutions for homes, shops, offices, factories, institutions, farmers and government project requirements.",

            "solutions_title": "Our Solutions",

            "solutions_description":
                "Electrical components, installation solutions, commissioning and service support for solar-related requirements.",

            "service_title": "Service Support",

            "service_description":
                "We provide installation, commissioning and ongoing service support according to customer requirements.",

            "location_heading": "Where We Are",

            "location_description":
                "Our head office is located in Lucknow, Uttar Pradesh.",

            "cta_label": "LET'S WORK TOGETHER",

            "cta_heading":
                "Looking for a Reliable Energy Solution?",

            "cta_description":
                "Get in touch with GARG GREEN ENERGY for your solar and renewable-energy requirements."
        }

        for field, default_value in defaults.items():

            current_value = existing_content[field]

            if current_value is None or not str(current_value).strip():

                connection.execute(
                    f"""
                    UPDATE website_content
                    SET {field} = ?
                    WHERE id = ?
                    """,
                    (
                        default_value,
                        existing_content["id"]
                    )
                )

    connection.commit()

    connection.close()


# ==================================================
# WEBSITE CONTENT HELPER
# ==================================================

def get_website_content():

    connection = get_db_connection()

    content = connection.execute("""
        SELECT *
        FROM website_content
        ORDER BY id ASC
        LIMIT 1
    """).fetchone()

    connection.close()

    return content


# ==================================================
# ADMIN AUTHENTICATION
# ==================================================

def admin_required(route_function):

    @wraps(route_function)
    def protected_route(*args, **kwargs):

        if not session.get("admin_logged_in"):

            return redirect(
                url_for("admin_login")
            )

        return route_function(*args, **kwargs)

    return protected_route


# ==================================================
# PUBLIC WEBSITE
# ==================================================

@app.route("/")
def home():

    connection = get_db_connection()

    reviews = connection.execute("""
        SELECT *
        FROM reviews
        WHERE status = 'Approved'
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    content = get_website_content()

    return render_template(
        "index.html",
        reviews=reviews,
        content=content
    )


@app.route("/about")
def about():

    content = get_website_content()

    return render_template(
        "about.html",
        content=content
    )


@app.route("/projects")
def projects():

    content = get_website_content()

    return render_template(
        "projects.html",
        content=content
    )


@app.route("/faq")
def faq():

    content = get_website_content()

    return render_template(
        "faq.html",
        content=content
    )


# ==================================================
# CONTACT / ENQUIRY
# ==================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        requirement = request.form.get(
            "requirement",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        if not name or not phone or not requirement:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("contact")
            )

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO enquiries
            (
                name,
                phone,
                email,
                location,
                requirement,
                message
            )
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

        return redirect(
            url_for("contact")
        )

    content = get_website_content()

    return render_template(
        "contact.html",
        content=content
    )


# ==================================================
# CUSTOMER REVIEWS
# ==================================================

@app.route("/review", methods=["GET", "POST"])
def review():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        rating = request.form.get(
            "rating",
            ""
        ).strip()

        review_text = request.form.get(
            "review",
            ""
        ).strip()

        if not name or not rating or not review_text:

            flash(
                "Please fill all review fields.",
                "error"
            )

            return redirect(
                url_for("review")
            )

        try:

            rating = int(rating)

        except ValueError:

            flash(
                "Please select a valid rating.",
                "error"
            )

            return redirect(
                url_for("review")
            )

        if rating < 1 or rating > 5:

            flash(
                "Rating must be between 1 and 5 stars.",
                "error"
            )

            return redirect(
                url_for("review")
            )

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO reviews
            (
                name,
                rating,
                review
            )
            VALUES (?, ?, ?)
        """, (
            name,
            rating,
            review_text
        ))

        connection.commit()
        connection.close()

        flash(
            "Thank you! Your review has been submitted for approval.",
            "success"
        )

        return redirect(
            url_for("review")
        )

    return render_template(
        "review.html"
    )


# ==================================================
# ADMIN LOGIN
# ==================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    connection = get_db_connection()

    total_enquiries = connection.execute("""
        SELECT COUNT(*) AS total
        FROM enquiries
    """).fetchone()["total"]

    new_enquiries = connection.execute("""
        SELECT COUNT(*) AS total
        FROM enquiries
        WHERE status = 'New'
    """).fetchone()["total"]

    pending_reviews = connection.execute("""
        SELECT COUNT(*) AS total
        FROM reviews
        WHERE status = 'Pending'
    """).fetchone()["total"]

    connection.close()

    return render_template(
        "admin_dashboard.html",
        total_enquiries=total_enquiries,
        new_enquiries=new_enquiries,
        pending_reviews=pending_reviews
    )


# ==================================================
# ADMIN ENQUIRIES
# ==================================================

@app.route("/admin/enquiries")
@admin_required
def admin_enquiries():

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    connection = get_db_connection()

    query = """
        SELECT *
        FROM enquiries
        WHERE 1 = 1
    """

    parameters = []

    if search:

        query += """
            AND (
                name LIKE ?
                OR phone LIKE ?
                OR email LIKE ?
                OR location LIKE ?
                OR requirement LIKE ?
                OR message LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    allowed_statuses = [
        "New",
        "Contacted",
        "In Progress",
        "Closed"
    ]

    if status in allowed_statuses:

        query += """
            AND status = ?
        """

        parameters.append(status)

    query += """
        ORDER BY id DESC
    """

    enquiries = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return render_template(
        "admin_enquiries.html",
        enquiries=enquiries,
        search=search,
        selected_status=status
    )


# ==================================================
# ADMIN ENQUIRY DETAILS
# ==================================================

@app.route(
    "/admin/enquiries/<int:enquiry_id>"
)
@admin_required
def admin_enquiry_detail(enquiry_id):

    connection = get_db_connection()

    enquiry = connection.execute("""
        SELECT *
        FROM enquiries
        WHERE id = ?
    """, (
        enquiry_id,
    )).fetchone()

    connection.close()

    if enquiry is None:

        flash(
            "Enquiry not found.",
            "error"
        )

        return redirect(
            url_for("admin_enquiries")
        )

    return render_template(
        "admin_enquiry_detail.html",
        enquiry=enquiry
    )


# ==================================================
# UPDATE ENQUIRY STATUS
# ==================================================

@app.route(
    "/admin/enquiries/<int:enquiry_id>/status",
    methods=["POST"]
)
@admin_required
def update_enquiry_status(enquiry_id):

    status = request.form.get(
        "status",
        ""
    ).strip()

    allowed_statuses = [
        "New",
        "Contacted",
        "In Progress",
        "Closed"
    ]

    if status not in allowed_statuses:

        flash(
            "Invalid enquiry status.",
            "error"
        )

        return redirect(
            url_for(
                "admin_enquiry_detail",
                enquiry_id=enquiry_id
            )
        )

    connection = get_db_connection()

    connection.execute("""
        UPDATE enquiries
        SET status = ?
        WHERE id = ?
    """, (
        status,
        enquiry_id
    ))

    connection.commit()
    connection.close()

    flash(
        "Enquiry status updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin_enquiry_detail",
            enquiry_id=enquiry_id
        )
    )


# ==================================================
# ADMIN REVIEWS
# ==================================================

@app.route("/admin/reviews")
@admin_required
def admin_reviews():

    status = request.args.get(
        "status",
        ""
    ).strip()

    connection = get_db_connection()

    if status in [
        "Pending",
        "Approved",
        "Rejected"
    ]:

        reviews = connection.execute("""
            SELECT *
            FROM reviews
            WHERE status = ?
            ORDER BY id DESC
        """, (
            status,
        )).fetchall()

    else:

        reviews = connection.execute("""
            SELECT *
            FROM reviews
            ORDER BY id DESC
        """).fetchall()

    connection.close()

    return render_template(
        "admin_reviews.html",
        reviews=reviews,
        selected_status=status
    )


# ==================================================
# UPDATE REVIEW STATUS
# ==================================================

@app.route(
    "/admin/reviews/<int:review_id>/status",
    methods=["POST"]
)
@admin_required
def update_review_status(review_id):

    status = request.form.get(
        "status",
        ""
    ).strip()

    allowed_statuses = [
        "Pending",
        "Approved",
        "Rejected"
    ]

    if status not in allowed_statuses:

        flash(
            "Invalid review status.",
            "error"
        )

        return redirect(
            url_for("admin_reviews")
        )

    connection = get_db_connection()

    connection.execute("""
        UPDATE reviews
        SET status = ?
        WHERE id = ?
    """, (
        status,
        review_id
    ))

    connection.commit()
    connection.close()

    flash(
        "Review status updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin_reviews")
    )


# ==================================================
# DELETE REVIEW
# ==================================================

@app.route(
    "/admin/reviews/<int:review_id>/delete",
    methods=["POST"]
)
@admin_required
def delete_review(review_id):

    connection = get_db_connection()

    connection.execute("""
        DELETE FROM reviews
        WHERE id = ?
    """, (
        review_id,
    ))

    connection.commit()
    connection.close()

    flash(
        "Review deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_reviews")
    )


# ==================================================
# ADMIN WEBSITE CONTENT
# ==================================================

@app.route(
    "/admin/content",
    methods=["GET", "POST"]
)
@admin_required
def admin_content():

    connection = get_db_connection()

    if request.method == "POST":

        # ----------------------------------------------
        # COMPANY INFORMATION
        # ----------------------------------------------

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        tagline = request.form.get(
            "tagline",
            ""
        ).strip()

        established = request.form.get(
            "established",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        # ----------------------------------------------
        # ABOUT PAGE
        # ----------------------------------------------

        about_label = request.form.get(
            "about_label",
            ""
        ).strip()

        about_heading = request.form.get(
            "about_heading",
            ""
        ).strip()

        about_description_1 = request.form.get(
            "about_description_1",
            ""
        ).strip()

        about_description_2 = request.form.get(
            "about_description_2",
            ""
        ).strip()

        # ----------------------------------------------
        # ABOUT HIGHLIGHTS
        # ----------------------------------------------

        focus_title = request.form.get(
            "focus_title",
            ""
        ).strip()

        focus_description = request.form.get(
            "focus_description",
            ""
        ).strip()

        solutions_title = request.form.get(
            "solutions_title",
            ""
        ).strip()

        solutions_description = request.form.get(
            "solutions_description",
            ""
        ).strip()

        service_title = request.form.get(
            "service_title",
            ""
        ).strip()

        service_description = request.form.get(
            "service_description",
            ""
        ).strip()

        # ----------------------------------------------
        # LOCATION
        # ----------------------------------------------

        location_heading = request.form.get(
            "location_heading",
            ""
        ).strip()

        location_description = request.form.get(
            "location_description",
            ""
        ).strip()

        head_office = request.form.get(
            "head_office",
            ""
        ).strip()

        other_location = request.form.get(
            "other_location",
            ""
        ).strip()

        # ----------------------------------------------
        # CTA
        # ----------------------------------------------

        cta_label = request.form.get(
            "cta_label",
            ""
        ).strip()

        cta_heading = request.form.get(
            "cta_heading",
            ""
        ).strip()

        cta_description = request.form.get(
            "cta_description",
            ""
        ).strip()

        # ----------------------------------------------
        # VALIDATION
        # ----------------------------------------------

        if not company_name:

            flash(
                "Company name is required.",
                "error"
            )

            connection.close()

            return redirect(
                url_for("admin_content")
            )

        # ----------------------------------------------
        # EXISTING CONTENT
        # ----------------------------------------------

        existing_content = connection.execute("""
            SELECT id
            FROM website_content
            ORDER BY id ASC
            LIMIT 1
        """).fetchone()

        if existing_content:

            connection.execute("""
                UPDATE website_content
                SET

                    company_name = ?,
                    tagline = ?,
                    established = ?,
                    description = ?,

                    about_label = ?,
                    about_heading = ?,
                    about_description_1 = ?,
                    about_description_2 = ?,

                    focus_title = ?,
                    focus_description = ?,

                    solutions_title = ?,
                    solutions_description = ?,

                    service_title = ?,
                    service_description = ?,

                    location_heading = ?,
                    location_description = ?,
                    head_office = ?,
                    other_location = ?,

                    cta_label = ?,
                    cta_heading = ?,
                    cta_description = ?,

                    updated_at = CURRENT_TIMESTAMP

                WHERE id = ?
            """, (

                company_name,
                tagline,
                established,
                description,

                about_label,
                about_heading,
                about_description_1,
                about_description_2,

                focus_title,
                focus_description,

                solutions_title,
                solutions_description,

                service_title,
                service_description,

                location_heading,
                location_description,
                head_office,
                other_location,

                cta_label,
                cta_heading,
                cta_description,

                existing_content["id"]
            ))

        else:

            connection.execute("""
                INSERT INTO website_content
                (
                    company_name,
                    tagline,
                    established,
                    description,

                    about_label,
                    about_heading,
                    about_description_1,
                    about_description_2,

                    focus_title,
                    focus_description,

                    solutions_title,
                    solutions_description,

                    service_title,
                    service_description,

                    location_heading,
                    location_description,
                    head_office,
                    other_location,

                    cta_label,
                    cta_heading,
                    cta_description
                )
                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?
                )
            """, (

                company_name,
                tagline,
                established,
                description,

                about_label,
                about_heading,
                about_description_1,
                about_description_2,

                focus_title,
                focus_description,

                solutions_title,
                solutions_description,

                service_title,
                service_description,

                location_heading,
                location_description,
                head_office,
                other_location,

                cta_label,
                cta_heading,
                cta_description
            ))

        connection.commit()
        connection.close()

        flash(
            "Website content updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin_content")
        )

    # ----------------------------------------------
    # LOAD CONTENT
    # ----------------------------------------------

    content = connection.execute("""
        SELECT *
        FROM website_content
        ORDER BY id ASC
        LIMIT 1
    """).fetchone()

    connection.close()

    return render_template(
        "admin_content.html",
        content=content
    )


# ==================================================
# ADMIN LOGOUT
# ==================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ==================================================
# INITIALIZE DATABASE
# ==================================================
# IMPORTANT:
# Gunicorn imports app.py instead of running it
# through "python app.py".
# Therefore database initialization must happen
# when the application module is loaded.

init_db()


# ==================================================
# LOCAL DEVELOPMENT
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )