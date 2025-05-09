from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from . import db, bcrypt
from app.models import Application, User, Job
from datetime import datetime

main = Blueprint('main', __name__)

# ---------------- Home Page ----------------
@main.route('/')
def home():
    return render_template('index.html')


# ---------------- Register ----------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        role = request.form['role']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match.")

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return render_template('register.html', error="Username or email already exists.")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password, role=role)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=f"Error creating account: {str(e)}")

    return render_template('register.html')


# ---------------- Login ----------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['email'] = user.email  # Store email in session
            session['username'] = user.username
            session['role'] = user.role

            if user.role == 'employer':
                return redirect(url_for('main.employer_dashboard'))
            elif user.role == 'job_seeker':
                return redirect(url_for('main.job_seeker_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))

        flash("Invalid credentials. Please try again.", 'error')
    return render_template('login.html')


# ---------------- Employer Dashboard ----------------
@main.route('/employer/dashboard')
def employer_dashboard():
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    employer_email = session['email']
    employer = User.query.filter_by(email=employer_email).first()
    jobs = Job.query.filter_by(employer_id=employer.id) if employer else []

    return render_template('employer_dashboard.html', jobs=jobs, username=session['username'])


# ---------------- Post a Job ----------------
@main.route('/employer/post', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        salary = request.form['salary']
        employer_email = session['email']

        # Find the employer by email to get the employer's ID
        employer = User.query.filter_by(email=employer_email).first()

        if employer:
            new_job = Job(title=title, description=description, location=location, salary=salary, employer_id=employer.id)
            db.session.add(new_job)
            db.session.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('main.employer_dashboard'))
        else:
            flash('Employer not found.', 'error')

    return render_template('post_job.html')


# ---------------- Delete Job ----------------
@main.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if session.get('role') not in ['employer', 'admin']:
        return redirect(url_for('main.login'))

    job = Job.query.get_or_404(job_id)
    employer = User.query.filter_by(email=session.get('email')).first()

    if employer and (session['role'] == 'admin' or job.employer_id == employer.id):
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'success')
    else:
        flash('You are not authorized to delete this job.', 'error')

    if session['role'] == 'admin':
        return redirect(url_for('main.manage_jobs'))
    elif session['role'] == 'employer':
        return redirect(url_for('main.employer_dashboard'))


# ---------------- Apply to Job (Job Seeker) ----------------
@main.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_for_job(job_id):
    if session.get('role') != 'job_seeker':
        return redirect(url_for('main.login'))

    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = session.get('email')
        phone = request.form.get('phone')
        cover_letter = request.form.get('cover_letter')
        resume_link = request.form.get('resume_link')

        application = Application(
            job_id=job.id,
            name=name,
            email=email,
            phone=phone,
            cover_letter=cover_letter,
            resume_link=resume_link
        )

        db.session.add(application)
        db.session.commit()

        flash('Application submitted successfully!', 'success')
        return redirect(url_for('main.job_seeker_dashboard'))

    return render_template('apply_for_job.html', job=job)


# ---------------- View Applications (Employer) ----------------
@main.route('/employer/job/<int:job_id>/applications', methods=['GET', 'POST'])
def view_applications(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()

    if request.method == 'POST':
        application_id = request.form.get('application_id')
        action = request.form.get('action')

        application = Application.query.get_or_404(application_id)

        if action == 'accept':
            application.status = 'Accepted'
        elif action == 'reject':
            application.status = 'Rejected'
            rejection_reason = request.form.get('rejection_reason')
            application.rejection_reason = rejection_reason

        try:
            db.session.commit()
            flash(f'Application {action.capitalize()}ed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating application: {str(e)}', 'error')

        return redirect(url_for('main.view_applications', job_id=job_id))

    return render_template('view_applications.html', job=job, applications=applications)


# ---------------- Job Seeker Dashboard ----------------
@main.route('/job_seeker/dashboard')
def job_seeker_dashboard():
    if session.get('role') != 'job_seeker':
        return redirect(url_for('main.login'))

    jobs = Job.query.all()
    return render_template('job_seeker_dashboard.html', jobs=jobs, username=session['username'])


# ---------------- View My Applications ----------------
@main.route('/job_seeker/applications')
def my_applications():
    if 'email' not in session:
        flash("Please log in to view your applications.")
        return redirect(url_for('main.login'))

    applications = Application.query.filter_by(email=session['email']).all()
    return render_template('my_applications.html', applications=applications)


# ---------------- Admin Dashboard ----------------
@main.route('/admin/dashboard')
def admin_dashboard():
    total_users = User.query.count()
    total_jobs = Job.query.count()
    pending_applications = Application.query.filter_by(status='Pending').count()
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_jobs=total_jobs,
                           pending_applications=pending_applications)


# ---------------- Manage Users ----------------
@main.route('/admin/manage_users')
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)


# ---------------- Manage Jobs ----------------
@main.route('/admin/manage_jobs', methods=['GET', 'POST'])
def manage_jobs():
    if session.get('role') != 'admin':
        return redirect(url_for('main.login'))

    jobs = Job.query.all()

    if request.method == 'POST':
        job_id = request.form.get('job_id')
        action = request.form.get('action')

        job = Job.query.get_or_404(job_id)

        if action == 'delete':
            db.session.delete(job)
            db.session.commit()
            flash('Job deleted successfully!', 'success')

        elif action == 'update':
            job.title = request.form.get('title', job.title)
            job.description = request.form.get('description', job.description)
            job.location = request.form.get('location', job.location)
            job.salary = request.form.get('salary', job.salary)

            db.session.commit()
            flash('Job updated successfully!', 'success')

    return render_template('manage_jobs.html', jobs=jobs)


# ---------------- Add User ----------------
@main.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if password:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    else:
        flash("Password is required!")
        return redirect(url_for('main.manage_users'))

    new_user = User(username=username, email=email, password=password_hash, role=role)

    try:
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully!", 'success')
        return redirect(url_for('main.manage_users'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding user: {e}", 'error')
        return redirect(url_for('main.manage_users'))


# ---------------- Delete User ----------------
@main.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.manage_users'))


# ---------------- View Applications (Admin) ----------------
@main.route('/admin/applications', methods=['GET', 'POST'])
def admin_view_applications():
    if session.get('role') != 'admin':
        return redirect(url_for('main.login'))

    applications = Application.query.all()

    if request.method == 'POST':
        application_id = request.form.get('application_id')
        action = request.form.get('action')

        application = Application.query.get_or_404(application_id)

        if action == 'accept':
            application.status = 'Accepted'
        elif action == 'reject':
            application.status = 'Rejected'
            rejection_reason = request.form.get('rejection_reason')
            application.rejection_reason = rejection_reason

        try:
            db.session.commit()
            flash(f'Application {action.capitalize()}ed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating application: {str(e)}', 'error')

        return redirect(url_for('main.admin_view_applications'))

    return render_template('admin_view_applications.html', applications=applications)


@main.route('/admin/application/<int:application_id>/update/<action>', methods=['POST'])
def admin_update_application_status(application_id, action):
    if session.get('role') != 'admin':
        return redirect(url_for('main.login'))

    application = Application.query.get_or_404(application_id)

    if action == 'accept':
        application.status = 'Accepted'
    elif action == 'reject':
        application.status = 'Rejected'
        rejection_reason = request.form.get('rejection_reason')
        application.rejection_reason = rejection_reason

    try:
        db.session.commit()
        flash(f'Application {action.capitalize()}ed successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'error')

    return redirect(url_for('main.admin_view_applications'))


# ---------------- Logout ----------------
@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))
