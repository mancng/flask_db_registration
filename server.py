from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import md5

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]*$')
PASS_REGEX = re.compile(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$')

app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
mysql = MySQLConnector(app,"registration_db")

@app.route('/')
def index():
    if 'user_id' in session:
        del session['user_id']
    else:
        session['login'] = False
        # users = mysql.query_db("SELECT * FROM users")
        # for user in users:
        #     print user['first_name']
    return render_template('index.html')

@app.route('/login')
def login():
    session['login'] = True
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def authenticate():
    errors = False
    if 'user_id' in session:
        del session['user_id']

    #Validate Email
    if not EMAIL_REGEX.match(request.form['email']):
        flash("***Invalid Email Address!", "email_err")
        errors = True

    #Validate Password character count
    if len(request.form['password']) < 8:
        flash("***Password must be more than 8 characters.", "pass_err")
        errors = True

    #Validate Confirm Password
    if request.form['password_con'] != request.form['password']:
        flash("***Confirm password doesn't match!")
        errors = True

    if errors:
        session['login'] = True
        return render_template('index.html')
    else:
        password = request.form['password']
        hashed_password = md5.new(password).hexdigest()

        enteredEmail = request.form['email']
        try:
            userInfo = mysql.query_db("SELECT * FROM users WHERE email = '" + str(enteredEmail) +"'")
            userInfo = userInfo[0]

            if str(userInfo['password']) == str(hashed_password):
                session['user_id'] = userInfo['id']
                session['first_name'] = userInfo['first_name']
                print "USER ID: ", session['user_id']
                return redirect('/success')
            else:
                flash("Email or Password do not match with system records")
                return render_template('index.html')
        except IndexError:
            flash("Email or Password do not match with system records")
            return render_template('index.html')

    

@app.route('/process', methods=['POST'])
def submit():
    errors = False
    #Validate Blank Fields
    if len(request.form['name_first']) < 1 or len(request.form['name_last']) < 1 or len(request.form['email']) < 1 or len(request.form['password']) < 1 or len(request.form['password_con']) < 1:
        flash("***All fields are mandatory and cannot be blank.", "all_err")
        errors = True

    #Validate Email
    if not EMAIL_REGEX.match(request.form['email']):
        flash("***Invalid Email Address!", "email_err")
        errors = True

    #Validate First and Last Names
    if len(request.form['name_first']) < 2 or len(request.form['name_last']) < 2:
        flash("Name must be at least 2 characters")
    elif not NAME_REGEX.match(request.form['name_first']) or not NAME_REGEX.match(request.form['name_last']):
        flash("***First Name or Last Name cannot contain any numbers", "name_err")
        errors = True

    #Validate Password character count
    if len(request.form['password']) < 8:
        flash("***Password must be more than 8 characters.", "pass_err")
        errors = True
    # elif not PASS_REGEX.match(request.form['password']):
    #     flash("***Password must contain at least 1 uppercase letter and 1 numeric value.")

    #Validate Confirm Password
    if request.form['password_con'] != request.form['password']:
        flash("***Confirm password doesn't match!")
        errors = True

    name_first = request.form['name_first']
    name_last = request.form['name_last']
    email = request.form['email']

    if errors:
        return redirect('/')
    else:
        password = request.form['password']
        hashed_password = md5.new(password).hexdigest()

        query = ("INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (:first_name, :last_name, :email, :password, NOW())")

        data = {
            "first_name" : name_first,
            "last_name" : name_last,
            "email" : email,
            "password" : hashed_password
        }

        session['user_id'] = mysql.query_db(query, data)
        session['first_name'] = name_first
        print "USER ID: ", session['user_id']

        return redirect('/success')

@app.route('/success')
def success():
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    del session['user_id']
    # session['login'] = False
    return render_template('index.html')

app.run(debug=True)