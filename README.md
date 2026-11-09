# Job Application Tracker

This is a web application I created for my COP 4751 project to help organize and track job applications during the job search process.

## Features

- **Dashboard:** Displays the total number of companies, jobs, applications, and contacts.
- **Companies:** Add, view, edit, and delete company information.
- **Jobs:** Keep track of job listings, including job titles, descriptions, salaries, and posting links.
- **Applications:** Track application dates, statuses, resumes, and interview information.
- **Contacts:** Store recruiter and company contact information.
- **Job Match:** Enter skills to find matching jobs, see match percentages, and identify missing skills.
- **JSON Data:** Uses JSON columns in MySQL to store job requirements and interview details.

## Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- GitHub

## Database

The application uses four main tables:

- `companies`
- `jobs`
- `applications`
- `contacts`

The tables are connected using foreign keys. The database also includes JSON columns for job requirements and interview information.

The `schema.sql` file contains the SQL needed to create the database tables.


## How to Run the Project

### Requirements

- Python 3
- MySQL Server
- MySQL Workbench (optional)
- Git (optional)

### Setup Instructions

1. Download or clone this GitHub repository.

2. Open the project folder in VS Code or a terminal.

3. Install the required Python packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Open MySQL Workbench or another MySQL client.

5. Import `schema.sql` into MySQL to create the `job_tracker` database and its tables. Use a fresh database because the script contains DROP TABLE statements.

6. Set the `DB_PASSWORD` environment variable to your local MySQL root password.

   In Windows PowerShell:

   ```powershell
   $env:DB_PASSWORD = "YOUR_MYSQL_PASSWORD"
   ```

7. Start the Flask application:

   ```powershell
   python app.py
   ```

8. Open the following address in your browser:

   http://127.0.0.1:5000

### Notes

- The database connection uses the local MySQL server and the `job_tracker` database.
- Database passwords are not stored in the GitHub repository.
- The `schema.sql` file creates the database structure but does not include sample records.
- Job Match results require jobs with requirements stored in the database.