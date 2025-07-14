from flask import render_template, url_for, flash, redirect, request, abort
from home import app, db, bcrypt, mail
from home.db_models import User, Goal
from home.forms import RegistrationForm, LoginForm, UpdateAccountForm, GoalForm, RequestResetForm, ResetPasswordForm
from PIL import Image 
import secrets
import os
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/home")
@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    goals = Goal.query.order_by(Goal.date_time.desc()).paginate(page=page, per_page=2)
    return render_template("home.html", title="FundFlow", goals=goals)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    '''if current_user.is_authenticated:
        return redirect(url_for('home'))'''
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    '''if current_user.is_authenticated:
        return redirect(url_for('home'))'''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful','success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email 
    image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route("/goal/new", methods=['GET', 'POST'])
@login_required
def new_goal():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            title=form.title.data, 
            description=form.description.data, 
            target_amount=form.target_amount.data,
            deadline=form.deadline.data,
            category=form.category.data,
            status=form.status.data,
            user_id=current_user.id
        )
        db.session.add(goal)
        db.session.commit()
        flash('Your goal has been created!', 'success')
        return redirect(url_for('home'))
    return render_template("create_goal.html", title="New Goal", form=form, legend='New Goal')

@app.route("/goal/<int:goal_id>")
@login_required
def goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    return render_template('goal.html', title=goal.title, goal=goal)

@app.route("/goal/<int:goal_id>/update", methods=['GET', 'POST'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)
    form = GoalForm()
    if form.validate_on_submit():
        goal.title = form.title.data
        goal.description = form.description.data
        goal.target_amount = form.target_amount.data
        goal.deadline = form.deadline.data
        goal.category = form.category.data
        goal.status = form.status.data
        db.session.commit()
        flash('Your goal has been updated!', 'success')
        return redirect(url_for('goal', goal_id=goal_id))
    elif request.method == 'GET':
        form.title.data = goal.title
        form.description.data = goal.description
        form.target_amount.data = goal.target_amount
        form.deadline.data = goal.deadline
        form.category.data = goal.category
        form.status.data = goal.status
    return render_template("create_goal.html", title="Update Goal", form=form, legend='Update Goal')

@app.route("/goal/<int:goal_id>/delete", methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        abort(403)
    db.session.delete(goal)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_goals(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.date_time.desc()).paginate(page=page, per_page=2)
    return render_template("user_goals.html", goals=goals, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='goldendawndebcaf@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request')) 
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)