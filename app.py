from flask import *
from sqlalchemy.sql.selectable import Exists
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from model import *


app = Flask ( __name__ )

#engine = create_engine('sqlite:///database.db', echo=True)
#engine = create_engine('postgresql://postgres:1sebaQuinta@localhost:5432/Gym', echo=False)
engine = create_engine('postgresql://postgres:Simone01@localhost:5432/Gym', echo=False)
#engine = create_engine('postgresql://postgres:gemellirosa@localhost:5432/Gym', echo=True)

app.config ['SECRET_KEY'] = 'ubersecret'

Session = sessionmaker(bind=engine, autoflush=True)

login_manager = LoginManager()
login_manager.init_app(app)

def truncate_message(string):
    if "ERRORE" in string:
        string = string.split("ERRORE: ",1)[1]
        string = string.split("CONTEXT: ",1)[0]
    return string

#__________________________________________ SESSION-USER ________________________________________


class SessionUser(UserMixin):
    # costruttore di classe
    def __init__(self, id, email, pwd, roles, active=True):
        self.id = id
        self.email = email
        self.pwd = pwd
        self.roles = roles
        self.active = active

def get_SessionUser_by_email(session, email):
    user = get_user(session, email = email)
    if user is not None:
        roles = [role.name for role in user.roles]
        return SessionUser(id=user.id, email=user.email, pwd=user.pwd, roles=roles)


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    try:
        user = get_user(session, id = user_id)
        if user is not None:
            roles = [role.name for role in user.roles]
            session.commit()
            return SessionUser(id=user.id, email=user.email, pwd=user.pwd, roles=roles)
    except:
        session.rollback()
        raise
    finally:
        session.close()

def is_admin(us):
    return us.is_authenticated and "Admin" in us.roles

def is_trainer(us):
    return us.is_authenticated and "Trainer" in us.roles


#__________________________________________ LOGIN ________________________________________


@app.route('/login')
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        return render_template("login.html")
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        return render_template("login.html")


@app.route('/login_form', methods=['POST'])
def login_form():
    if request.method == 'POST':
        session = Session()
        try:
            userReq = request.form['user']
            passReq = request.form['pass']
            userIn = get_user(session, email = userReq)
            if(userIn is not None):
                if (passReq == userIn.pwd):
                    user = get_SessionUser_by_email(session, userReq)
                    login_user(user)
                    session.commit()
                    flash("Login completed successfully", category='success')
                    return redirect(url_for('login'))
                else:
                    raise BaseException("Wrong password")
            else:
                raise BaseException("email " + userReq + " doesn't exists")
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('login'))
        finally:
            session.close()


#__________________________________________ SIGNUP ________________________________________


@app.route('/signup')
def signup():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('private'))
        return render_template("signup.html")
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        return redirect(url_for('signup'))

@app.route('/signin_form', methods=['POST'])
def signin_form():
    if request.method == 'POST':
        session = Session()
        try:
            fullname = request.form['name']
            email = request.form['email']
            address = request.form['address']
            telephone = request.form['telephone']
            pwd1 = request.form['pwd1']
            pwd2 = request.form['pwd2']
            us = get_user(session, email=email)
            if not fullname:
                raise BaseException("Please enter a fullname")
            elif not email:
                raise BaseException("Please enter an email")
            elif not telephone:
                raise BaseException("Please enter telephone")
            elif not address:
                raise BaseException("Please enter address")
            elif us is not None:
                raise BaseException("email " + email + " already exists")
            elif not pwd1:
                raise BaseException("Please enter a password")
            elif len(pwd1) < 6:
                raise BaseException("Password must contain more than 6 characters")
            elif pwd1 != pwd2: 
                raise BaseException("Passwords do not match")
            else:
                for user in get_user(session, all=True):
                    if telephone == user.telephone:
                        raise BaseException("Phone number " + telephone + " already exixsts")
                add_user(session, fullname=fullname, email=email, address=address, telephone=telephone, pwd=pwd1)
                user = get_SessionUser_by_email(session, email)
                login_user(user)
                session.commit()
                flash("Signed in successfully.", category='success')
                return redirect(url_for('signup'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('signup'))
        finally:
            session.close()


#__________________________________________ LOGOUT ________________________________________


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


#__________________________________________ HOME ________________________________________


@app.route('/')
def home():
    try:
        return render_template("home.html")
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            return redirect(url_for('home'))


# ________________________________________________________ PRIVATE ________________________________________________________


@app.route('/private')
@login_required
def private():

    session = Session()

    def new_messages():
        messages = get_message(session, addresser=current_user.id)
        new = False
        for message in messages:
            new |= (not message.read)
        return new

    try:
        user = get_user(session, email=current_user.email)
        resp = make_response(render_template("private.html", us = user, new_mess=new_messages()))
        session.commit()
        return resp
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/private/prenotations')
@login_required
def prenotations():
    session = Session() 
    try:
        user = get_user(session, email=current_user.email)
        shifts = filter(lambda sh: (sh.date == datetime.date.today() and datetime.datetime.now().time() <= sh.ending) or sh.date > datetime.date.today(), user.shifts)
        shifts = sorted(shifts, key=lambda sh: (sh.date, sh.starting))
        return make_response(render_template("prenotations.html", shifts=shifts))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('prenotations'))
    finally:
        session.close()


@app.route('/private/courses_sign_up')
@login_required
def courses_sign_up():
    session = Session() 
    try:
        user = get_user(session, email=current_user.email)
        courses = user.courses
        return make_response(render_template("courses_sign_up.html", courses=courses, today=datetime.date.today()))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('courses_sign_up'))
    finally:
        session.close()


@app.route('/private/covid_report')
@login_required
def covid_report():
    session = Session() 
    try:
        user = get_user(session, id=current_user.id)
        user_covid_report(session, user_id=user.id)
        session.commit()
        return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/private/messages')
@login_required
def messages():
    session = Session() 
    try:
        messages = get_message(session, addresser=current_user.id)
        resp = make_response(render_template("messages.html", messages=list(reversed(messages))))
        mark_read(session, messages)
        session.commit()
        return resp
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('messages'))
    finally:
        session.close()


@app.route('/private/messages/del/<mess_id>', methods=['POST'])
@login_required
def delete_message(mess_id):
    if request.method == 'POST':
        session = Session()
        try:
            del_message(session, id=mess_id)
            session.commit()
            return redirect(url_for('messages'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('messages'))
        finally:
            session.close()


# ________________________________________________________ UPDATE USER ________________________________________________________


@app.route('/private/update_user')
@login_required
def upd_user():
    session = Session()
    try:
        user = get_user(session, id = current_user.id)
        return render_template("update_user.html", user = user)
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('upd_user'))
    finally:
        session.close()


@app.route('/private/update_user_form', methods=['POST'])
@login_required
def update_user_form():
    if request.method == 'POST':
        session = Session()
        try:
            user = get_user(session, email= current_user.email)
            fullname = request.form['fullname']
            if not fullname:
                raise BaseException("Empty fullname!")
            telephone = request.form['telephone']
            if not telephone:
                raise BaseException("Empty telephone!")
            for us in get_user(session, all=True):
                if telephone == us.telephone and user.email != us.email:
                    raise BaseException("Phone number " + telephone + " already exixsts")
            address = request.form['address']
            if not address:
                raise BaseException("Empty address!")
            pwd1 = request.form['pwd1']
            if not pwd1:
                raise BaseException("Empty password!")
            pwd2 = request.form['pwd2']
            if not pwd2:
                raise BaseException("Empty password!")
            if pwd1 != pwd2:
                raise BaseException("Password Mismatch!")     
            update_user(session, user_id = user.id, fullname = fullname, telephone = telephone, address = address, pwd = pwd1)
            session.commit()
            return redirect(url_for('private'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('upd_user'))
        finally:
            session.close()


# ________________________________________________________ SHIFT, PRENOTATION ________________________________________________________

@app.route('/shifts')
def shifts():
    session = Session()
    try:
        year = request.args.get('year')
        month = request.args.get('month')
        day = request.args.get('day')
        room = request.args.get('room')
        date = datetime.date(year=int(year), month=int(month), day=int(day))
        if date < datetime.date.today():
            date = datetime.date.today()
        date_string = date.strftime("%Y-%m-%d")
        settings = get_week_setting(session, day_name=date.strftime("%A"))
        if settings is None:
            resp = make_response(render_template("shifts.html", shifts=[], date_string=date_string, rooms=get_room(session, all=True), user=None))
        else:
            length = timedelta(hours=settings.length.hour,   minutes=settings.length.minute)
            start = timedelta(hours=settings.starting.hour,   minutes=settings.starting.minute)
            end_ = timedelta(hours=settings.ending.hour,   minutes=settings.ending.minute)
            shifts = []
            if room == 'All':
                for r in get_room(session, all=True):
                    end = start + length 
                    while (end <= end_):
                        shifts.append(
                            [date,
                            datetime.time(hour=(end-length).seconds//3600, minute=((end-length).seconds//60)%60), 
                            datetime.time(hour=end.seconds//3600, minute=(end.seconds//60)%60),
                            r,
                            r.max_capacity,
                            None]
                        )
                        end += length
            else:
                r = get_room(session, name=room)
                end = start + length 
                while (end <= end_):
                    shifts.append(
                        [date,
                        datetime.time(hour=(end-length).seconds//3600, minute=((end-length).seconds//60)%60), 
                        datetime.time(hour=end.seconds//3600, minute=(end.seconds//60)%60),
                        r,
                        r.max_capacity,
                        None]
                    )
                    end += length
            shifts = [s for s in filter(lambda s: get_shift(session, date=date, start=s[1], room_id=s[3].id) is None or get_shift(session, date=date, start=s[1], room_id=s[3].id).course_id is None, shifts)] # Remove the shifts occupied from a course
            if date == date.today():
                shifts = [s for s in filter(lambda s: s[1] >= datetime.datetime.now().time(), shifts)]
            for s in shifts:
                mem_shift = get_shift(session, date=date, start=s[1], room_id=s[3].id)
                if mem_shift is not None:
                    s[4] = s[4] - len(mem_shift.prenotations)
                    s[5] = mem_shift
            if current_user.is_authenticated:
                user = get_user(session, id=current_user.id)
            else:
                user = None
            resp = make_response(render_template("shifts.html", shifts=sorted(shifts, key=lambda t: (t[1], t[3].id)), date_string=date_string, rooms=get_room(session, all=True), user=user))
        session.commit()
        return resp
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('shifts_first'))
    finally:
        session.close()


@app.route('/shifts/shifts_first')
def shifts_first():
    curr = datetime.date.today()
    return redirect('/shifts?year=%s&month=%s&day=%s&room=All' % (curr.year, curr.month, curr.day))


@app.route('/shifts/load_date', methods=['POST'])
def shifts_load_state():
    if request.method == 'POST':
        session = Session()
        try:
            date_str = request.form['date']
            room = request.form['room']
            date_str = date_str.replace('-', '/')
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
            session.commit()
            return redirect('/shifts?year=%s&month=%s&day=%s&room=%s' % (date.year, date.month, date.day, room))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('shifts_first'))
        finally:
            session.close()


@app.route('/prenotation', methods=['POST'])
def prenotation():
    if request.method == 'POST':
        session = Session()
        try:
            if current_user.is_authenticated:
                us = get_user(session, id = current_user.id)
                shift_id = int(request.form['shift_id'])
                if shift_id != -1:
                    s = get_shift(session, id = shift_id)
                else:
                    date = request.form['date']
                    start = request.form['start']
                    end = request.form['end']
                    room_id = request.form['room_id']
                    add_shift(session, date=date, start=start, end=end, room_id=room_id)
                    s = get_shift(session, date=date, start=start, room_id=room_id)
                add_prenotation(session, user = us, shift = s)
                session.commit()
                return redirect(url_for('prenotations'))
            session.commit()
            return redirect(url_for('login'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            if current_user.is_authenticated:
                return redirect(url_for('shifts_first'))
            return redirect(url_for('login'))
        finally:
            session.close()
    

@app.route('/del_prenotation/<shift>')
@login_required
def del_prenotation(shift):
    session = Session()
    try:
        us = get_user(session,id = current_user.id)
        s = get_shift(session, id = shift)
        delete_prenotation(session, shift=s, user=us)
        session.commit()
        return redirect(url_for('prenotations'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('prenotations'))
    finally:
        session.close()

# ________________________________________________________COURSES________________________________________________________


@app.route('/courses')
def courses():
    session = Session()
    try:
        courses = get_course(session, all=True)
        if is_trainer(current_user):
            user = get_user(session, email=current_user.email)
            courses = filter(lambda course: course not in user.trainer.courses, courses)
        session.commit()
        return render_template("courses.html", courses = courses, today= datetime.date.today())
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('courses'))
    finally:
        session.close()


@app.route('/courses/course/<course_name>')
def course(course_name):
    session = Session()
    try:
        course = get_course(session, name = course_name)
        sh = []
        for cp in course.course_programs:
            ws = cp.week_setting
            starting = time_to_timedelta(ws.starting) + time_to_timedelta(ws.length) * (cp.turn_number-1)
            ending = starting + time_to_timedelta(ws.length)
            sh.append(Shift(
                date=datetime.date.today(), # not used
                starting = starting,
                ending = ending,
                room_id = cp.room_id,
                course_id = course.id
            ))
        if current_user.is_authenticated:
            user = get_user(session, id = current_user.id)
            cs = get_course_sign_up(session, user_id=user.id, course_id=course.id)
            session.commit()
            return render_template("course.html", course = course, shifts=sh, has_sign_up= (cs is not None))
        else:
            session.commit()
            return render_template("course.html", course = course, shifts=sh)
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('course', course_name=course_name))
    finally:
        session.close()


@app.route('/courses/sign_up/<course_name>')
def sign_up(course_name):
    session = Session()
    try:
        if current_user.is_authenticated:
            us = get_user(session, id = current_user.id)
            c = get_course(session, name= course_name)
            add_course_sign_up(session, user=us, course=c)
            session.commit()
            flash("SignUp completed successfully", category='success')
            return redirect(url_for('courses_sign_up'))
        session.commit()
        return redirect(url_for('login'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('course', course_name = course_name))
    finally:
        session.close()


@app.route('/courses/delete_sign_up/<course_name>')
@login_required
def delete_sign_up(course_name):
    session = Session()
    try:
        us = get_user(session,id = current_user.id)
        c = get_course(session, name = course_name)
        delete_course_sign_up(session,course = c, user = us)
        session.commit()
        flash("SignUp deleted successfully", category='success')
        return redirect(url_for('courses_sign_up'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('course', course_name=course_name))
    finally:
        session.close()


#__________________________________ TRAINER COURSES __________________________________


@app.route('/courses/courses/trainer_courses')
@login_required
def trainer_courses():
    session = Session()
    try:
        user = get_user(session, email=current_user.email)
        if is_trainer(current_user):
            courses = user.trainer.courses
            session.commit()
            return render_template("trainer_courses.html", courses = courses, trainer = user.trainer, today= datetime.date.today())
        session.commit()
        return redirect(url_for('courses'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_trainer(current_user):
            return redirect(url_for('trainer_courses'))
        return redirect(url_for('courses'))
    finally:
        session.close()


@app.route('/courses/courses/trainer_course/<course_name>')
@login_required
def trainer_course(course_name):

    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            sh = []
            for cp in course.course_programs:
                ws = cp.week_setting
                starting = time_to_timedelta(ws.starting) + time_to_timedelta(ws.length) * (cp.turn_number-1)
                ending = starting + time_to_timedelta(ws.length)
                sh.append(Shift(
                    date=datetime.date.today(), # not used
                    starting = starting,
                    ending = ending,
                    room_id = cp.room_id,
                    course_id = course.id
                ))
            session.commit()
            return render_template("trainer_course.html", course = course, course_program = course.course_programs, shifts = sh)
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('trainer_course', course_name=course_name))
    finally:
        session.close()


@app.route('/courses/delete_course/<course_name>', methods=['POST'])
@login_required
def del_course(course_name):
    if request.method == 'POST':
        session = Session()
        try:
            trainer = get_trainer(session, email = current_user.email)
            course = get_course(session, name=course_name)
            if is_trainer(current_user) and course.instructor_id == trainer.id:
                delete_course(session, course_id = course.id)
                session.commit()
                return redirect(url_for('trainer_courses'))
            session.commit()
            return redirect(url_for('courses'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('trainer_course'), course_name=course_name)
        finally:
            session.close()


@app.route('/courses/new_course')
@login_required
def new_course():
    session = Session()
    try:
        if is_trainer(current_user):
            r = get_room(session, all=True)
            session.commit()
            return render_template('add_course.html', rooms=r)
        session.commit()
        return redirect(url_for('courses'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_trainer(current_user):
            return redirect(url_for('new_course'))
        return redirect(url_for('courses'))
    finally:
        session.close()


@app.route('/courses/new_course_form', methods=['POST'])
@login_required
def new_course_form():
    if request.method == 'POST':
        session = Session()
        try:
            if is_trainer(current_user):
                name = request.form['name']
                starting = request.form['starting']
                ending = request.form['ending']
                max_partecipants = request.form['max_partecipants']
                if not name:
                    raise BaseException("Please enter name")
                elif not starting:
                    raise BaseException("Please enter starting")
                elif not ending:
                    raise BaseException("Please enter ending")
                elif not starting < ending:
                    raise BaseException("Course starts after his ending")
                elif not max_partecipants:
                    raise BaseException("Please enter max partecipants")
                elif get_course(session, name=name) is not None:
                    raise BaseException(name + " Course already exists")
                else:
                    instructor_id = current_user.id
                    add_course(session, name=name, starting=starting, ending=ending, max_partecipants=max_partecipants, instructor_id=instructor_id)
                    session.commit()
                    return redirect(url_for('new_program', course_name = name))
            else:
                session.commit()
                return redirect(url_for('courses'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('new_course'))
        finally:
            session.close()


@app.route('/courses/new_course/new_program/<course_name>')
@login_required
def new_program(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            rooms = get_room(session, all=True)
            r = {}
            for room in rooms:
                r[room.id] = room.name
            session.commit()
            return render_template('new_program.html', course = get_course(session, name=course_name), room_dict = r)
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('new_program', course_name=course_name))
    finally:
        session.close()


@app.route('/courses/undo_course/<course_name>')
@login_required
def undo_course(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        c = get_course(session, name=course_name)
        if is_trainer(current_user) and c.instructor_id == trainer.id:
            starting = c.starting
            ending = c.ending
            max_partecipants = c.max_partecipants
            delete_course(session, course_id=c.id)
            session.commit()
            return render_template('add_course.html', rooms=get_room(session, all=True), course_name=course_name, starting=starting, ending=ending, max_partecipants=max_partecipants)
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('new_course'))
    finally:
        session.close()


@app.route('/courses/new_course/add_program/<course_name>')
@login_required
def add_program(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            r = get_room(session, all=True)
            session.commit()
            return render_template('add_program.html', rooms = r, course = get_course(session, name=course_name), week_setting = get_week_setting(session, all=True))
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('add_program', course_name=course_name))
    finally:
        session.close()


@app.route('/courses/new_course/add_program_form/<course_name>', methods=['POST'])
@login_required
def add_program_form(course_name):

    def to_second(t):
        return (t.hour * 60 + t.minute) * 60 + t.second

    if request.method == 'POST':
        session = Session()
        try:
            trainer = get_trainer(session, email = current_user.email)
            c = get_course(session, name=course_name)
            if is_trainer(current_user) and c.instructor_id == trainer.id:
                room = request.form['room']
                r = get_room(session, name = room)
                day = request.form['day']
                course_id = c.id
                tn = request.form['turn_number']
                ws = get_week_setting(session, day_name=day)
                tn = clamp(int(tn), 1, (to_second(ws.ending) - to_second(ws.starting) ) / to_second(ws.length))
                add_course_program(session, week_day=day, turn_number=tn, room_id=r.id, course_id=course_id )
                session.commit()
                return redirect(url_for('new_program', course_name = course_name))
            else:
                session.commit()
                return redirect(url_for('courses'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('add_program', course_name=course_name))
        finally:
            session.close()


@app.route('/courses/new_course/del_program/<program_id>/<course_name>')
@login_required
def del_program(program_id, course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            delete_course_program(session, cp_id=int(program_id))
            session.commit()
            return redirect(url_for('new_program', course_name = course_name))
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('new_program', course_name = course_name))
    finally:
        session.close()

@app.route('/courses/new_course/plan_course/<course_name>')
@login_required
def plan_course_(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name=course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            plan_course(session, course_name)
            session.commit()
            flash("Course " + course_name + " created successfully", category='success')
            return redirect(url_for('trainer_course', course_name=course_name))
        else:
            session.commit()
            return redirect(url_for('courses'))
    
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('new_program', course_name = course_name))
    finally:
        session.close()


#____________________________________ UPDATE COURSE ____________________________________


@app.route('/update_course/<course_name>')
@login_required
def upd_course(course_name):
    session = Session()
    try:
        trainer = get_trainer(session, email = current_user.email)
        course = get_course(session, name= course_name)
        if is_trainer(current_user) and course.instructor_id == trainer.id:
            session.commit()
            return render_template('update_course.html', course=course)
        else:
            session.commit()
            return redirect(url_for('courses'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('upd_course', course_name = course_name))
    finally:
        session.close()


@app.route('/update_course_form/<course_name>', methods=["POST"])
@login_required
def upd_course_form(course_name):
    if request.method == 'POST':
        session = Session()
        try:
            trainer = get_trainer(session, email = current_user.email)
            course = get_course(session, name=course_name)
            if is_trainer(current_user) and course.instructor_id == trainer.id:
                courses = get_course(session, all=True)
                
                name = request.form['name']
                if not name:
                    raise BaseException("Please enter name")    
                for i in courses:
                    if i.name == name and i.name != course_name:
                        raise BaseException(name + " course already exists!")    

                max_partecipants = int(request.form['max_partecipants'])
                if not max_partecipants:
                    raise BaseException("Please enter max partecipants")  
    
                update_course(session, course_id=course.id, name=name, max_partecipants=max_partecipants) # trigger controlli
                session.commit()
                return redirect(url_for('trainer_course', course_name = name))
            else:
                session.commit()
                return redirect(url_for('courses'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('upd_course', course_name = course_name))
        finally:
            session.close()        


# ________________________________________________________ADMIN SETTINGS________________________________________________________

@app.route('/admin/settings/global_settings')
@login_required
def global_settings():
    session = Session()
    try:
        if is_admin(current_user):
            global_settings = get_global_setting(session, all=True)
            global_settings = sorted(global_settings, key=lambda x: x.name)
            resp= make_response(render_template("update_global_settings.html", global_settings=global_settings))
            session.commit()
            return resp
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for("global_settings"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/global_settings_form', methods=['POST'])
@login_required
def global_settings_form():
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):
                global_settings = get_global_setting(session, all=True)
                for global_setting in global_settings:
                    val = int(request.form[global_setting.name])
                    if not val:
                        raise BaseException("Please enter " + global_setting.name + " value")
                    if val != global_setting.value:
                        update_global_setting(session, name=global_setting.name, value=val)
                session.commit()
                flash("Global Settings Updated successfully", category='success')
                return redirect(url_for('private'))
            else:
                session.commit()
                return redirect(url_for('private')) 
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for("global_settings"))
        finally:
            session.close()


@app.route('/admin/users_info')
@login_required
def users_info():
    session = Session()
    try:
        if is_admin(current_user):
            users = get_user(session, all=True)
            users = filter(lambda us: us.email != 'admin@gmail.com', users)
            session.commit()
            return make_response(render_template("users_info.html", users=users))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('users_info'))
    finally:
        session.close()

@app.route('/admin/covid_states')
@login_required
def covid_states():
    session = Session()
    try:
        if is_admin(current_user):
            cs0 = filter(lambda us: us.covid_state == 0, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            cs1 = filter(lambda us: us.covid_state == 1, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            cs2 = filter(lambda us: us.covid_state == 2, filter(lambda us: us.email != 'admin@gmail.com',  get_user(session, all=True)))
            session.commit()
            return make_response(render_template("covid_states.html", cs0=cs0, cs1=cs1, cs2=cs2))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('covid_states'))
    finally:
        session.close()


#_____________________________________ ROOM SETTINGS _____________________________________


@app.route('/admin/settings/room_settings')
@login_required
def room_settings():
    session = Session()
    try:
        if is_admin(current_user):
            rooms = get_room(session, all=True)
            rooms = sorted(rooms, key=lambda x: x.id)
            resp= make_response(render_template("update_room_settings.html", rooms=rooms))
            session.commit()
            return resp
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for('room_settings'))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/rooms_settings_form/<room_id>', methods=['POST'])
@login_required
def room_settings_form(room_id):
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):
                room = get_room(session, id=room_id)
                val = int(request.form[str(room_id)])
                if not val:
                    raise BaseException("Please enter room_capacity")   
                if val != room.max_capacity:
                    update_room_max_capacity(session, name=room.name, mc=val)
                session.commit()
                return redirect(url_for('room_settings'))
            else:
                session.commit()
                return redirect(url_for('private'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for("room_settings"))
        finally:
            session.close()


@app.route('/admin/settings/room_settings/add_room')
@login_required
def add_room_():
    session = Session()
    try:
        if is_admin(current_user):
            session.commit()
            return make_response(render_template("add_room.html"))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for("add_room_"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/room_settings/add_room_form', methods=['POST'])
@login_required
def add_room_form():
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):  
                name = request.form['name']
                max_capacity = request.form['max_capacity']
                if not name:
                    raise BaseException("Please enter name")  
                elif not max_capacity:
                    raise BaseException("Please enter max_capacity")
                elif get_room(session, name=name) is not None:
                    raise BaseException("Room " + name + " already exists")   
                add_room(session, name=name, max_capacity=max_capacity)
                session.commit()
                flash("Room " + name + " added succesfully", category='success')
                return redirect(url_for('room_settings'))
            else:
                session.commit()
                return redirect(url_for('private'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for("add_room_"))
        finally:
            session.close()


@app.route('/admin/settings/room_settings/delete_room/<room_id>')
@login_required
def del_room(room_id):
    session = Session()
    try:
        if is_admin(current_user):
            delete_room(session, room_id=int(room_id))
            session.commit()
            return redirect(url_for('room_settings'))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('room_settings'))
    finally:
        session.close()


#_____________________________________ USER SETTINGS _____________________________________


@app.route('/admin/settings/user_settings/user/<user_id>')
@login_required
def user_settings(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            user = get_user(session, id=user_id)
            for role in user.roles:
                print(role.name)
            session.commit()
            return make_response(render_template("user_settings.html", user=user, isStaff=(get_role(session,name="Trainer") in user.roles)))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for('user_settings', user_id=user_id))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()


@app.route('/admin/settings/user_settings_form', methods=['POST'])
@login_required
def users_settings_form():
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):
                user_id = request.form['user']
                session.commit()
                return redirect(url_for('user_settings', user_id=user_id))
            else:
                session.commit()
                return redirect(url_for('private'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('user_settings', user_id=user_id))
        finally:
            session.close()


@app.route('/admin/settings/user_settings/user/reset_covid_state/<user_id>')
@login_required
def reset_covid_state(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            update_user(session=session, user_id=user_id, covid_state=0)
            session.commit()
            return redirect(url_for('user_settings', user_id=user_id))         
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('user_settings', user_id=user_id))
    finally:
        session.close()


@app.route('/admin/settings/new_deadline/<user_id>', methods=["POST"])
@login_required
def new_deadline(user_id):
    if request.method == 'POST':
        session = Session()
        try:
            if is_admin(current_user):
                date_str = request.form["date"]
                date_str = date_str.replace('-', '/')
                date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
                if date.date() <= get_user(session, id=user_id).subscription:
                    raise BaseException("Subscription can only be posponed")
                update_user(session, user_id=user_id, subscription=date)
                session.commit()
                return redirect(url_for('user_settings', user_id=user_id))
            else:
                session.close()
                return redirect(url_for('private'))
        except BaseException as exc:
            flash(truncate_message(str(exc)), category='error')
            session.rollback()
            return redirect(url_for('user_settings', user_id=user_id))
        finally:
            session.close()


@app.route('/admin/settings/user_settings/assign_trainer_role/<user_id>')
@login_required
def assign_trainer_role_(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            assign_trainer_role(session, user_id=user_id)
            session.commit()
            return redirect(url_for('user_settings', user_id=user_id))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('user_settings'), user_id=user_id)
    finally:
        session.close()


@app.route('/admin/settings/user_settings/revoke_trainer_role/<user_id>')
@login_required
def revoke_trainer_role_(user_id):
    session = Session()
    try:
        if is_admin(current_user):
            revoke_trainer_role(session, user_id=user_id)
            session.commit()
            return redirect(url_for('user_settings', user_id=user_id))
        else:
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        return redirect(url_for('user_settings', user_id=user_id))
    finally:
        session.close()


@app.route('/admin/settings/week_settings')
@login_required
def week_settings():
    session = Session()
    try:
        if is_admin(current_user):
            global_settings = { 
                "Opening":str(get_global_setting(session, name="HourOpening").value) + ":00", 
                "Closing":str(get_global_setting(session, name="HourClosing").value) + ":00",
                "MaxShiftLength":get_global_setting(session, name="MaximumShiftLength").value,
                "MinShiftLength":get_global_setting(session, name="MinimumShiftLength").value
                }
            week_settings = get_week_setting(session, all=True)
            convert = {'Monday' : 0, 'Tuesday' : 1, 'Wednesday' : 2, 'Thursday' : 3, 'Friday' : 4, 'Saturday' : 5, 'Sunday' : 6}
            week_settings.sort(key=lambda t: convert[t.day_name])
            resp = make_response(render_template("week_settings.html", week_settings=week_settings, global_settings=global_settings))
            session.commit()
            return resp
        else:
            session.commit()
            return redirect(url_for("private"))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for("week_settings"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()

@app.route('/admin/settings/week_settings_form/<day_name>', methods=['POST'])
@login_required
def week_Settings_form(day_name):
    session = Session()
    try:
        if request.method == 'POST':
            if is_admin(current_user):                
                starting = datetime.datetime.strptime(request.form['Starting'], "%H:%M:%S").time()
                ending = datetime.datetime.strptime(request.form['Ending'], "%H:%M:%S").time()
                length = datetime.datetime.strptime(request.form['Shifts Length'], "%H:%M:%S").time()
                update_weekend_setting(session, day_name=day_name, starting=starting, ending=ending, length=length)
                flash("Week Settings Updated successfully", category='success')        
            session.commit()
            return redirect(url_for('private'))
    except BaseException as exc:
        flash(truncate_message(str(exc)), category='error')
        session.rollback()
        if is_admin(current_user):
            return redirect(url_for("week_settings"))
        else:
            return redirect(url_for('private'))
    finally:
        session.close()

