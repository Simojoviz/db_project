from flask import Flask
from flask import *

from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

import sys
sys.path.append('../pyscript')
from model import *


app = Flask ( __name__ )

#engine = create_engine('sqlite:///database.db', echo=True)
engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
# engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=True)
#engine = create_engine('postgresql://postgres:gemellirosa@localhost:5432/Gym', echo=True)


app.config ['SECRET_KEY'] = 'ubersecret'


Session = sessionmaker(bind=engine, autoflush=True)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, psw, active=True):
        self.id = id
        self.email = email
        self.psw = psw
        self.active = active

def get_user_by_email(session, email):
    user = get_user(session, email = email)
    if user is not None:
        return User(user.id, user.email, user.pwd)

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = get_user(session, id = user_id)
    session.close()
    if user is not None:
        return User(user.id, user.email, user.pwd)

@app.route('/')
def home():
    session = Session()
    try:
        #if current_user.is_authenticated:
            #return redirect(url_for('private'))
        users = get_user(session, all=True)
        session.commit()
        return render_template("home.html", users=users)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/prenotations')
@login_required
def prenotations():
    session = Session() 
    try:
        email = current_user.email
        user = get_user(session, email=email)
        shifts = user.prenotations_shifts
        resp = make_response(render_template("prenotations.html", prenotations=shifts))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/private/courses_sign_up')
@login_required
def courses_sign_up():
    session = Session() 
    try:
        email = current_user.email
        user = get_user(session, email=email)
        courses = user.courses
        resp = make_response(render_template("courses_sign_up.html", courses=courses))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses')
def courses():
    try:
        session = Session()
        courses = get_course(session, all=True)
        return render_template("courses.html", courses = courses)
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/courses/<course_name>')
def course(course_name):
    session = Session()
    c = get_course(session,name = course_name)
    cp = get_course_program(session,course_id = c.id)
    sh = []
    for i in cp:
        sh.append(get_shift(session, id=i.turn_number))
    return render_template("course.html", course = c, course_program = cp, shift = sh)

@app.route('/sign_up/<course_name>')
def sign_up(course_name):
    session = Session()
    if current_user.is_authenticated:
        us = get_user(session, id = current_user.id)
        c = get_course(session, name= course_name)
        add_course_sign_up(session, user=us, course=c)
        session.commit()
        return redirect(url_for('courses_sign_up'))
    return redirect(url_for('login'))

@app.route('/delete_sign_up/<course_name>')
def delete_sign_up(course_name):
    session = Session()
    us = get_user(session,id = current_user.id)
    c = get_course(session, name = course_name)
    cs = delete_course_sign_up(session,course = c, user = us)
    return redirect(url_for('courses_sign_up'))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/login_form', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        session = Session()
        try:
            userReq = request.form['user']
            passReq = request.form['pass']
            userIn = get_user(session, email = userReq)
            if(userIn is not None):
                if (passReq == userIn.pwd):
                    user = get_user_by_email(session, userReq)
                    login_user(user)
                    session.commit()
                    return redirect(url_for('login'))
                else:
                    session.commit()
                    return redirect(url_for('login'))
            else:
                session.commit()
                return redirect(url_for('login'))
        except:
            session.rollback()
            raise
        finally:
            session.close()


@app.route('/private')
@login_required
def private():
    session = Session()
    try:
        email = current_user.email
        user = get_user(session, email=email)
        shifts = user.prenotations_shifts
        resp = make_response(render_template("private.html", us = user))
        session.commit()
        return resp
    except:
        session.rollback()
        raise
    finally:
        session.close()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))