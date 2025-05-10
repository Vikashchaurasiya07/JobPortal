# Job Portal Web Application

This is a Job Portal web application built using Flask, SQLite, HTML, CSS, and Bootstrap. It supports multiple user roles: Job Seekers, Employers, and Admins. The platform allows job seekers to register, search jobs, and apply, while employers can post jobs and manage job listings. Admins have the ability to manage users and jobs.

## Features

- **Job Seekers**
  - Register and login to create a profile.
  - Search and filter job listings.
  - Apply for jobs directly through the portal.

- **Employers**
  - Post job listings and manage job applications.
  - View and manage job posts from a dashboard.

- **Admin**
  - Admin dashboard to manage users and job posts.
  - Ability to delete/edit users and job posts.
  - Manage site settings.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLite

## Installation

### Prerequisites
- Python 3.x
- Flask
- SQLite3

### Steps

1. Clone the repository:
    ```bash
    git clone <your-repository-url>
    ```

2. Navigate to the project directory:
    ```bash
    cd job-portal
    ```

3. Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Run the Flask app:
    ```bash
    python app.py
    ```

6. Open the browser and go to `http://127.0.0.1:5000` to see the application.

## Screenshots

Add your screenshots in the `screenshots/` folder, and refer to them here:

![Landing page]![image](https://github.com/user-attachments/assets/d3d57227-364d-460c-b18f-c3c072910e97)

![Job Seekers]![image](https://github.com/user-attachments/assets/1c2b3d23-a1cb-4e72-9864-6d5a9e51c0fb)

![Employer_panel]![image](https://github.com/user-attachments/assets/28c74c7f-72e6-4e88-9cbb-af6f0a246eaf)

![Admin Panel](![image](https://github.com/user-attachments/assets/6f279bf7-658e-42c8-a84c-471410c9b540)
)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
