from flask import render_template, url_for, flash, redirect, request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from todo_project import app, db, bcrypt

# Import the forms
from todo_project.forms import (LoginForm, RegistrationForm, UpdateUserInfoForm, 
                                UpdateUserPassword, TaskForm, UpdateTaskForm)

# Import the Models
from todo_project.models import User, Task

# Import 
from flask_login import login_required, current_user, login_user, logout_user
from todo_project.observability import record_http_request, record_user_action


@app.after_request
def collect_http_metrics(response):
    endpoint = request.endpoint or 'unknown'
    record_http_request(endpoint, request.method, response.status_code)
    return response


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.errorhandler(404)
def error_404(error):
    return (render_template('errors/404.html'), 404)

@app.errorhandler(403)
def error_403(error):
    return (render_template('errors/403.html'), 403)

@app.errorhandler(500)
def error_500(error):
    return (render_template('errors/500.html'), 500)


@app.route("/")
@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        app.logger.info('login skipped: already authenticated user=%s', current_user.username)
        return redirect(url_for('all_tasks'))

    form = LoginForm()
    # After you submit the form
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Check if the user exists and the password is valid
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            task_form = TaskForm()
            flash('Login Successfull', 'success')
            record_user_action('login', 'success')
            app.logger.info('login success user=%s', user.username)
            return redirect(url_for('all_tasks'))
        else:
            flash('Login Unsuccessful. Please check Username Or Password', 'danger')
            record_user_action('login', 'failure')
            app.logger.warning('login failure username=%s', form.username.data)
    
    return render_template('login.html', title='Login', form=form)
    

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        app.logger.info('logout user=%s', current_user.username)
        record_user_action('logout', 'success')
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        app.logger.info('register skipped: already authenticated user=%s', current_user.username)
        return redirect(url_for('all_tasks'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created For {form.username.data}', 'success')
        record_user_action('register', 'success')
        app.logger.info('register success user=%s', form.username.data)
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route("/all_tasks")
@login_required
def all_tasks():
    tasks = User.query.filter_by(username=current_user.username).first().tasks
    return render_template('all_tasks.html', title='All Tasks', tasks=tasks)


@app.route("/add_task", methods=['POST', 'GET'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(content=form.task_name.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Task Created', 'success')
        record_user_action('task_create', 'success')
        app.logger.info('task created user=%s task=%s', current_user.username, form.task_name.data)
        return redirect(url_for('add_task'))
    return render_template('add_task.html', form=form, title='Add Task')


@app.route("/all_tasks/<int:task_id>/update_task", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = UpdateTaskForm()
    if form.validate_on_submit():
        if form.task_name.data != task.content:
            task.content = form.task_name.data
            db.session.commit()
            flash('Task Updated', 'success')
            record_user_action('task_update', 'success')
            app.logger.info('task updated user=%s task_id=%s', current_user.username, task_id)
            return redirect(url_for('all_tasks'))
        else:
            flash('No Changes Made', 'warning')
            record_user_action('task_update', 'no_change')
            return redirect(url_for('all_tasks'))
    elif request.method == 'GET':
        form.task_name.data = task.content
    return render_template('add_task.html', title='Update Task', form=form)


@app.route("/all_tasks/<int:task_id>/delete_task")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task Deleted', 'info')
    record_user_action('task_delete', 'success')
    app.logger.info('task deleted user=%s task_id=%s', current_user.username, task_id)
    return redirect(url_for('all_tasks'))


@app.route("/account", methods=['POST', 'GET'])
@login_required
def account():
    form = UpdateUserInfoForm()
    if form.validate_on_submit():
        if form.username.data != current_user.username:  
            current_user.username = form.username.data
            db.session.commit()
            flash('Username Updated Successfully', 'success')
            record_user_action('account_update', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username 

    return render_template('account.html', title='Account Settings', form=form)


@app.route("/account/change_password", methods=['POST', 'GET'])
@login_required
def change_password():
    form = UpdateUserPassword()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.session.commit()
            flash('Password Changed Successfully', 'success')
            record_user_action('password_change', 'success')
            redirect(url_for('account'))
        else:
            flash('Please Enter Correct Password', 'danger') 
            record_user_action('password_change', 'failure')

    return render_template('change_password.html', title='Change Password', form=form)

