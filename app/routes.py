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
                return redirect(url_for('main.home'))

        flash("Invalid credentials. Please try again.", 'error')
    return render_template('login.html')


# ---------------- Employer Dashboard ----------------
@main.route('/employer/dashboard')
def employer_dashboard():
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    employer_email = session['email']
    employer = User.query.filter_by(email=employer_email).first()  # Get the employer by email
    if employer:
        jobs = Job.query.filter_by(employer_id=employer.id).all()  # Filter jobs by employer_id
    else:
        jobs = []

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
        employer_email = session['email']  # Get employer's email from session

        new_job = Job(title=title, description=description, location=location, salary=salary, employer_email=employer_email)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('main.employer_dashboard'))

    return render_template('post_job.html')


# ---------------- Delete Job ----------------
@main.route('/employer/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    job = Job.query.get_or_404(job_id)
    if job.employer_email == session['email']:  # Compare with employer's email in session
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully!', 'success')

    return redirect(url_for('main.employer_dashboard'))


# ---------------- Apply to Job (Job Seeker) ----------------
@main.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_for_job(job_id):
    if session.get('role') != 'job_seeker':
        return redirect(url_for('main.login'))

    job = Job.query.get_or_404(job_id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = session.get('email')  # Get the email from session
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
        # Handle Accept or Reject actions
        application_id = request.form.get('application_id')
        action = request.form.get('action')

        application = Application.query.get_or_404(application_id)

        if action == 'accept':
            application.status = 'Accepted'
        elif action == 'reject':
            application.status = 'Rejected'
            rejection_reason = request.form.get('rejection_reason')
            application.rejection_reason = rejection_reason  # Store the reason for rejection

        try:
            db.session.commit()
            flash(f'Application {action.capitalize()}ed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating application: {str(e)}', 'error')

        return redirect(url_for('main.view_applications', job_id=job_id))

    return render_template('view_applications.html', job=job, applications=applications)

# ---------------- Application Status Update (Accept/Reject) ----------------
@main.route('/employer/application/update', methods=['POST'])
def update_application_status():
    if session.get('role') != 'employer':
        return redirect(url_for('main.login'))

    application_id = request.args.get('application_id')  # Get application_id from URL query parameter
    action = request.args.get('action')  # Get the action (e.g., 'reject', 'accept')

    if not application_id or not action:
        flash('Invalid request.', 'error')
        return redirect(url_for('main.employer_dashboard'))

    application = Application.query.get_or_404(application_id)  # Get the application by ID

    # Validate the action and update the application status
    if action == 'reject':
        application.status = 'Rejected'
        flash('Application rejected successfully!', 'success')
    elif action == 'accept':
        application.status = 'Accepted'
        flash('Application accepted successfully!', 'success')
    else:
        flash('Invalid action.', 'error')

    try:
        db.session.commit()  # Commit the changes to the database
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating application: {str(e)}', 'error')

    return redirect(url_for('main.view_applications', job_id=application.job_id))  # Redirect to the job's application page




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

    applications = Application.query.filter_by(email=session['email']).all()  # Filter by email from session
    return render_template('my_applications.html', applications=applications)


# ---------------- Logout ----------------
@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))
