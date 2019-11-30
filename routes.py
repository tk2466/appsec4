from datetime import datetime
import os
import subprocess
from flask import render_template, url_for, redirect, request

from werkzeug.utils import escape

from app import db
from forms import *
from models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        if current_user.username.lower()=='admin':
            sh = Spelling_History.query.all()
        else:
            user_id=current_user.id
            sh = Spelling_History.query.filter_by(user_id=user_id).all()
        return render_template('home.html', sh=sh)
    else:
        return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('spell_check'))

    form = RegistrationForm()
    username = escape(form.username.data)
    password = escape(form.password.data)
    phonenumber = escape(form.phonenumber.data)

    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(password).decode('utf-8')
        if form.username.data.lower() == 'Admin'.lower():
            role='Admin'
        else:
            role='User'
        user=User(username=username, password=hashed_pwd, phonenumber=phonenumber, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('spell_check'))

    form = LoginForm()
    result = "Please login!"

    username = escape(form.username.data)
    password = escape(form.password.data)

    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):

            now=datetime.utcnow()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

            ses = Session(user_id=user.id, login=date_time, logout="N/A")
            db.session.add(ses)
            db.session.commit()

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('spell_check'))
        else:
            result = "Username or Password is incorrect or Two-factor authentication failure"
            return render_template("login.html", title='Login',form=form, result=result)
    return render_template('login.html', title='Login', form=form, result=result)


@app.route("/spell_check", methods=['GET', 'POST'])
@login_required
def spell_check():
    form=CheckSpelling()

    if request.method == 'GET':
        return render_template("spell_check.html", title='Spelling Checker', form=form)

    if form.validate_on_submit():
        currpath = os.getcwd()
        inputtext = escape(form.inputtext.data)

        # Writting the user input to .txt file for a.out
        inputfile = open("./static/userinput.txt", "w")
        inputfile.writelines(inputtext)
        inputfile.close()

        tmp = subprocess.check_output(
            [currpath + '/static/a.out', currpath + '/static/userinput.txt', currpath + '/static/wordlist.txt']).decode(
            'utf-8')
        tmp = tmp.replace("\n", ", ")[:-2]

        spell = Spelling_History(query_text=inputtext, query_result=tmp, checker=current_user)
        db.session.add(spell)
        db.session.commit()
        return render_template("spell_check.html", title='Spelling Checker', form=form, misspelled=tmp, outputtext=inputtext)


@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():

    if current_user.username.lower() != 'admin':
        user_id = current_user.id
        allids = Spelling_History.query.filter_by(user_id=user_id).all()
        numqueries = Spelling_History.query.filter_by(user_id=user_id).count()
        return render_template('non_admin_history.html', title='Spell Check History', numqueries=numqueries, allids=allids)
    else:
        form = HistoryForm()

        if request.method == 'GET':
            return render_template("history.html", title='Spell Check History', form=form)

        if form.validate_on_submit():
            username=escape(form.username.data)
            user_id = User.query.filter_by(username=username).first().id
            allids = Spelling_History.query.filter_by(user_id=user_id).all()
            numqueries = Spelling_History.query.filter_by(user_id=user_id).count()
            return render_template('history.html', title='Spell Check History', form=form, numqueries=numqueries, allids=allids, username=username)


@app.route('/query/<int:qid>')
@login_required
def query(qid):
    sh = Spelling_History.query.get_or_404(qid)

    user = User.query.filter_by(id=sh.user_id).first()
    username = user.username
    querytext = sh.query_text
    queryresult = sh.query_result

    if current_user.username.lower()!='admin':
        if username.lower()!=current_user.username.lower():
            return redirect(url_for('history'))

    return render_template('query.html', title='Query ID:'+str(qid), queryid=qid, username=username, querytext=querytext, queryresult=queryresult)


@app.route('/login_history', methods=['GET', 'POST'])
@login_required
def login_history():

    if current_user.username.lower() != 'admin':
        return render_template('non_admin_login_history.html', title='Login History')
    else:
        form = LoginHistoryForm()

        if request.method == 'GET':
            return render_template("login_history.html", title='Login History', form=form)

        if form.validate_on_submit():
            user_id = escape(form.uid.data)
            allids = Session.query.filter_by(user_id=user_id).all()
            return render_template('login_history.html', title='Login History', form=form, allids=allids)


@app.route("/logout")
@login_required
def logout():

    now = datetime.utcnow()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    user_id=current_user.id
    user_session = db.session.query(Session).filter(Session.user_id==user_id, Session.logout=='N/A').first()
    user_session.logout = date_time
    db.session.commit()

    logout_user()
    return redirect(url_for('login'))