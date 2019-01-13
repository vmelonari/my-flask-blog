from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3
import os
from functools import wraps


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database.db'),
    HOST = "localhost",
    CURSORCLASS = "DictCursor",
    SECRET_KEY='12345',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
        con = sqlite3.connect(app.config["DATABASE"])
        con.row_factory = sqlite3.Row
        #get Articles

        cur = con.cursor()
        result = cur.execute("SELECT * FROM articles")

        articles = result.fetchall();

        if articles is not None:
            return render_template("articles.html", articles = articles)

        else:
            msg = "No Articles found!"
            return render_template("articles.html", msg = msg)

            #close Connection
        cur.close()

#single article
@app.route("/article/<string:id>")
def article(id):
        con = sqlite3.connect(app.config["DATABASE"])
        con.row_factory = sqlite3.Row
        #get Articles

        cur = con.cursor()
        result = cur.execute("SELECT * FROM articles WHERE ID = ?", (id))

        article = result.fetchone();

        return render_template("article.html", article = article)

            #close Connection
        cur.close()


class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=3, max=25)])
    email = StringField("E-Mail", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Password do not match")
    ])
    confirm = PasswordField("Confirm Password")

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #create cursors
        cur = sqlite3.connect(app.config["DATABASE"])
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(?, ?, ?, ?)", (name, email, username, password))

        # commit to DB
        cur.commit()

        # Close Connection
        cur.close()

        flash("You are now registered and can log in", "success")

        redirect(url_for("home"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #Get Form Fields
        username = request.form["username"]
        password_canditate = request.form["password"]

        c = sqlite3.connect(app.config["DATABASE"])
        c.row_factory = sqlite3.Row
        cur = c.cursor()

        #get user by USERNAME
        result = cur.execute("SELECT * FROM users WHERE username = ?", (username, ))

        if result is not None:
            # Get stored hash. Row 4 is the password data
            password = result.fetchone()["password"]
            # password = data[4]

            #compare passwords
            if sha256_crypt.verify(password_canditate, password):
                # passed
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Login"
                return render_template("login.html", error=error)
            #CLose DB Connection
            cur.close()

        else:
            error = "Username not found"
            return render_template("login.html", error=error)


    return render_template("login.html")

#checks if a user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Please log in", "danger")
            return redirect(url_for("login"))
    return wrap

@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))

#Dashboard
@app.route("/dashboard")
@is_logged_in
def dashboard():

    con = sqlite3.connect(app.config["DATABASE"])
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    #get Articles
    result = cur.execute("SELECT * FROM articles")

    articles = result.fetchall()

    if articles is not None:
        return render_template("dashboard.html", articles = articles)

    else:
        msg = "No Articles found!"
        return render_template("dashboard.html", msg = msg)

        #close Connection
    cur.close()


#Article Class form
class ArticleForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=200)])
    body = TextAreaField("Body", [validators.Length(min=30)])

@app.route("/add_article", methods=["POST", "GET"])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        cur = sqlite3.connect(app.config["DATABASE"])

        cur.execute("INSERT INTO articles(title, body, author) VALUES(?, ?, ?)", (title, body, session["username"]))

        cur.commit()

        cur.close()

        flash("Article created", "success")

        return redirect(url_for("dashboard"))

    return render_template("add_article.html", form=form)

#edit article
@app.route("/edit_article/<string:id>", methods=["POST", "GET"])
@is_logged_in
def edit_article(id):

    con = sqlite3.connect(app.config["DATABASE"])
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    #get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = ?", (id))

    article = result.fetchone()

    #get form
    form = ArticleForm(request.form)

    #populate article from fields
    form.title.data = article["title"]
    form.body.data = article["body"]

    if request.method == "POST" and form.validate():
        title = request.form["title"]
        body = request.form["body"]

        cur = sqlite3.connect(app.config["DATABASE"])

        cur.execute("UPDATE articles SET title = ?, body = ? WHERE id = ?", (title, body, id))

        cur.commit()

        cur.close()

        flash("Article updated", "success")

        return redirect(url_for("dashboard"))

    return render_template("edit_article.html", form=form)

#delete article
@app.route("/delete_article/<string:id>", methods=["POST"])
@is_logged_in
def delete_article(id):
    con = sqlite3.connect(app.config["DATABASE"])
    # con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("DELETE FROM articles WHERE ID = ?", (id))

    con.commit()

    cur.close()

    flash("Article deleted", "success")

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(threaded=True, debug=True)
