from chatterbot import ChatBot
from flask import Flask, render_template, request,session,logging, url_for,redirect,flash,jsonify
from flask_recaptcha import ReCaptcha
import mysql.connector
import os
import uuid
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

app = Flask(__name__)

recaptcha = ReCaptcha(app=app)
app.secret_key=os.urandom(24)
app.static_folder = 'static'

#Google keys
app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6LdbAx0aAAAAAANl04WHtDbraFMufACHccHbn09L",
    RECAPTCHA_SECRET_KEY = "6LdbAx0aAAAAAMmkgBKJ2Z9xsQjMD5YutoXC6Wee"
))

recaptcha=ReCaptcha()
recaptcha.init_app(app)

#app.config['SECRET_KEY'] = 'cairocoders-ednalan'
# Replace 'your_database_url' with the actual URL to your database
DATABASE_URL = 'mysql://sqluser:password@localhost/register'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the User model to represent the 'users' table
class User(Base):
    __tablename__ = 'users'
    email = Column(String,primary_key=True)
    hint = Column(String)

#database connectivity
conn=mysql.connector.connect(host='localhost',port='3306',user='sqluser',password='password',database='register',auth_plugin='mysql_native_password')
cur=conn.cursor()

def make_key():
    return uuid.uuid4()

@app.route("/index")
def home():
    if 'id' in session:
        return render_template('index.html')
    else:
        return redirect('/')

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/register')
def about():
    return render_template('register.html')

# Route to get hint based on email

@app.route('/get_hint', methods=['GET'])
def get_hint():
    email = request.args.get('email')
    
    if not email:
        return jsonify({"error": "Email parameter is missing."}), 400

    # Query the database using SQLAlchemy
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()

    if user:
        hint = user.hint
    else:
        hint = "No hint available for this email."

    return jsonify({"hint": hint})


@app.route('/login_validation',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    cur.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email,password))
    users = cur.fetchall()
    if len(users)>0:
        session['id']=users[0][0]
        flash('You were successfully logged in')
        return redirect('/index')
    else:
        flash('Invalid credentials !!!')
        return redirect('/')
    # return "The Email is {} and the Password is {}".format(email,password)
    # return render_template('register.html')

@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('name') 
    email=request.form.get('uemail')
    password=request.form.get('upassword')
    hint=request.form.get('hint')

    #cur.execute("UPDATE users SET password='{}'WHERE name = '{}'".format(password, name))
    cur.execute("""INSERT INTO  users(name,email,password,hint) VALUES('{}','{}','{}','{}')""".format(name,email,password,hint))
    conn.commit()
    cur.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}'""".format(email))
    myuser=cur.fetchall()
    flash('You have successfully registered!')
    session['id']=myuser[0][0]
    return redirect('/index')

@app.route('/suggestion',methods=['POST'])
def suggestion():
    email=request.form.get('uemail')
    suggesMess=request.form.get('message')

    cur.execute("""INSERT INTO  suggestion(email,message) VALUES('{}','{}')""".format(email,suggesMess))
    conn.commit()
    flash('You suggestion is succesfully sent!')
    return redirect('/index')

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')  
    return str(ChatBot.get_response(userText))

if __name__ == "__main__":
    # app.secret_key=""
    app.run(debug=True) 