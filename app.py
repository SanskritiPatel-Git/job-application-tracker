from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM companies")
    companies = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    jobs = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    applications = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM contacts")
    contacts = cursor.fetchone()["total"]


    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        companies=companies,
        jobs=jobs,
        applications=applications,
        contacts=contacts
    )

@app.route('/companies')
def companies_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT company_id, company_name, industry,
               website, city, state, notes
        FROM companies
        ORDER BY company_name
    """)

    companies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("companies.html", companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        website = request.form.get('website', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        notes = request.form.get('notes', '').strip()

        if not company_name or len(company_name) > 100:
            return "Please enter a company name (100 characters max).", 400

        if (len(industry) > 50 or len(website) > 200 or
                len(city) > 50 or len(state) > 50):
            return "One or more fields are too long.", 400

        if website and not website.startswith(('https://', 'http://')):
            return "Website must start with http:// or https://", 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO companies
                    (company_name, industry, website, city, state, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                company_name,
                industry or None,
                website or None,
                city or None,
                state or None,
                notes or None
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('companies_page'))

    return render_template('add_company.html')

@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
def edit_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM companies WHERE company_id = %s",
            (company_id,)
        )
        company = cursor.fetchone()

        if company is None:
            return "Company not found.", 404

        if request.method == 'POST':
            company_name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', '').strip()
            website = request.form.get('website', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            notes = request.form.get('notes', '').strip()

            if not company_name or len(company_name) > 100:
                return "Please enter a company name (100 characters max).", 400

            if (len(industry) > 50 or len(website) > 200 or
                    len(city) > 50 or len(state) > 50):
                return "One or more fields are too long.", 400

            if website and not website.startswith(('https://', 'http://')):
                return "Website must start with http:// or https://", 400

            cursor.execute("""
                UPDATE companies
                SET company_name = %s,
                    industry = %s,
                    website = %s,
                    city = %s,
                    state = %s,
                    notes = %s
                WHERE company_id = %s
            """, (
                company_name,
                industry or None,
                website or None,
                city or None,
                state or None,
                notes or None,
                company_id
            ))

            conn.commit()
            return redirect(url_for('companies_page'))

        return render_template('edit_company.html', company=company)

    finally:
        cursor.close()
        conn.close()

@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT company_id FROM companies WHERE company_id = %s",
            (company_id,)
        )

        if cursor.fetchone() is None:
            return "Company not found.", 404

        cursor.execute(
            "SELECT COUNT(*) AS total FROM jobs WHERE company_id = %s",
            (company_id,)
        )
        job_count = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM contacts WHERE company_id = %s",
            (company_id,)
        )
        contact_count = cursor.fetchone()["total"]

        if job_count > 0 or contact_count > 0:
            return (
                "This company cannot be deleted because it has "
                "related jobs or contacts. Remove those records first.",
                400
            )

        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )
        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('companies_page'))

@app.route('/jobs')
def jobs_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                jobs.job_id,
                jobs.job_title,
                companies.company_name,
                jobs.job_type,
                jobs.salary_min,
                jobs.salary_max,
                jobs.date_posted,
                jobs.posting_url AS job_url
            FROM jobs
            LEFT JOIN companies
                ON jobs.company_id = companies.company_id
            ORDER BY jobs.job_title
        """)

        jobs = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('jobs.html', jobs=jobs)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        company_id = request.form.get('company_id', '').strip()
        job_title = request.form.get('job_title', '').strip()
        job_type = request.form.get('job_type', '').strip()
        salary_min = request.form.get('salary_min', '').strip()
        salary_max = request.form.get('salary_max', '').strip()
        date_posted = request.form.get('date_posted', '').strip()
        posting_url = request.form.get('posting_url', '').strip()
        job_description = request.form.get('job_description', '').strip()

        if not company_id.isdigit():
            return "Please select a valid company.", 400

        if not job_title or len(job_title) > 100:
            return "Please enter a job title (100 characters max).", 400

        if job_type not in ('', 'Full-time', 'Part-time',
                            'Contract', 'Internship'):
            return "Please select a valid job type.", 400

        from decimal import Decimal, InvalidOperation

        try:
            minimum = Decimal(salary_min) if salary_min else None
            maximum = Decimal(salary_max) if salary_max else None
        except InvalidOperation:
            return "Please enter valid salary amounts.", 400

        for amount in (minimum, maximum):
            if amount is not None and (
                not amount.is_finite() or
                amount < 0 or
                amount > Decimal('99999999.99')
            ):
                return "Please enter a valid positive salary.", 400

        if minimum is not None and maximum is not None:
            if minimum > maximum:
                return "Minimum salary cannot exceed maximum salary.", 400

        if posting_url and not posting_url.startswith(
            ('https://', 'http://')
        ):
            return "Job URL must start with http:// or https://", 400

        if len(posting_url) > 500:
            return "Job URL is too long.", 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO jobs (
                    company_id, job_title, job_type,
                    salary_min, salary_max, date_posted,
                    posting_url, job_description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                int(company_id),
                job_title,
                job_type or None,
                minimum,
                maximum,
                date_posted or None,
                posting_url or None,
                job_description or None
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('jobs_page'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        companies = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('add_job.html', companies=companies)

@app.route('/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM jobs WHERE job_id = %s",
            (job_id,)
        )
        job = cursor.fetchone()

        if job is None:
            return "Job not found.", 404

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        companies = cursor.fetchall()

        if request.method == 'POST':
            from decimal import Decimal, InvalidOperation

            company_id = request.form.get('company_id', '').strip()
            job_title = request.form.get('job_title', '').strip()
            job_type = request.form.get('job_type', '').strip()
            salary_min = request.form.get('salary_min', '').strip()
            salary_max = request.form.get('salary_max', '').strip()
            date_posted = request.form.get('date_posted', '').strip()
            posting_url = request.form.get('posting_url', '').strip()
            job_description = request.form.get('job_description', '').strip()

            if not company_id.isdigit() or not any(
                c['company_id'] == int(company_id) for c in companies
            ):
                return "Please select a valid company.", 400

            if not job_title or len(job_title) > 100:
                return "Please enter a job title (100 characters max).", 400

            if job_type not in (
                '', 'Full-time', 'Part-time', 'Contract', 'Internship'
            ):
                return "Please select a valid job type.", 400

            try:
                minimum = Decimal(salary_min) if salary_min else None
                maximum = Decimal(salary_max) if salary_max else None
            except InvalidOperation:
                return "Please enter valid salary amounts.", 400

            for amount in (minimum, maximum):
                if amount is not None and (
                    not amount.is_finite()
                    or amount < 0
                    or amount > Decimal('99999999.99')
                ):
                    return "Please enter a valid positive salary.", 400

            if minimum is not None and maximum is not None:
                if minimum > maximum:
                    return "Minimum salary cannot exceed maximum salary.", 400

            if posting_url and not posting_url.startswith(
                ('https://', 'http://')
            ):
                return "Job URL must start with http:// or https://", 400

            if len(posting_url) > 500:
                return "Job URL is too long.", 400

            cursor.execute("""
                UPDATE jobs
                SET company_id = %s,
                    job_title = %s,
                    job_type = %s,
                    salary_min = %s,
                    salary_max = %s,
                    date_posted = %s,
                    posting_url = %s,
                    job_description = %s
                WHERE job_id = %s
            """, (
                int(company_id),
                job_title,
                job_type or None,
                minimum,
                maximum,
                date_posted or None,
                posting_url or None,
                job_description or None,
                job_id
            ))

            conn.commit()
            return redirect(url_for('jobs_page'))

        return render_template(
            'edit_job.html',
            job=job,
            companies=companies
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT job_id FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        if cursor.fetchone() is None:
            return "Job not found.", 404

        cursor.execute(
            "SELECT COUNT(*) AS total FROM applications WHERE job_id = %s",
            (job_id,)
        )

        application_count = cursor.fetchone()["total"]

        if application_count > 0:
            return (
                "This job cannot be deleted because it has "
                "applications connected to it.",
                400
            )

        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('jobs_page'))

@app.route('/applications')
def applications_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                applications.application_id,
                applications.application_date,
                applications.status,
                applications.resume_version,
                applications.cover_letter_sent,
                applications.response_date,
                applications.interview_date,
                applications.notes,
                jobs.job_title,
                companies.company_name
            FROM applications
            JOIN jobs
                ON applications.job_id = jobs.job_id
            JOIN companies
                ON jobs.company_id = companies.company_id
            ORDER BY applications.application_date DESC
        """)

        applications = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'applications.html',
        applications=applications
    )

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            job_id = request.form.get('job_id', '').strip()
            application_date = request.form.get(
                'application_date', ''
            ).strip()
            status = request.form.get('status', 'Applied').strip()
            resume_version = request.form.get(
                'resume_version', ''
            ).strip()
            cover_letter_sent = (
                1 if request.form.get('cover_letter_sent') == '1'
                else 0
            )
            response_date = request.form.get(
                'response_date', ''
            ).strip()
            interview_date = request.form.get(
                'interview_date', ''
            ).strip()

            notes = request.form.get('notes', '').strip()

            interview_type = request.form.get('interview_type', '').strip()
            interviewer = request.form.get('interviewer', '').strip()
            interview_location = request.form.get('interview_location', '').strip()
            interview_feedback = request.form.get('interview_feedback', '').strip()

            if len(interviewer) > 100 or len(interview_location) > 200:
                return "Interview details are too long.", 400

            valid_interview_types = (
                '', 'Phone', 'Video', 'In Person',
                'Technical', 'Behavioral'
            )

            if interview_type not in valid_interview_types:
                return "Please select a valid interview type.", 400

            import json

            interview_details = {
                'interview_type': interview_type,
                'interviewer': interviewer,
                'location': interview_location,
                'feedback': interview_feedback
            }

            interview_data = (
                json.dumps(interview_details)
                if any(interview_details.values())
                else None
            )

            if not job_id.isdigit():
                return "Please select a valid job.", 400

            cursor.execute(
                "SELECT job_id FROM jobs WHERE job_id = %s",
                (int(job_id),)
            )
            if cursor.fetchone() is None:
                return "The selected job does not exist.", 400

            from datetime import date, datetime

            try:
                applied_on = date.fromisoformat(application_date)
                responded_on = (
                    date.fromisoformat(response_date)
                    if response_date else None
                )
                interviewed_on = (
                    datetime.fromisoformat(interview_date)
                    if interview_date else None
                )
            except ValueError:
                return "Please enter valid dates.", 400

            valid_statuses = (
                'Applied', 'Screening', 'Interview',
                'Offer', 'Rejected', 'Withdrawn'
            )
            if status not in valid_statuses:
                return "Please select a valid status.", 400

            if len(resume_version) > 50:
                return "Resume version is too long.", 400


            cursor.execute("""
                INSERT INTO applications (
                    job_id, application_date, status, resume_version,
                    cover_letter_sent, response_date, interview_date,
                    notes, interview_data
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                int(job_id),
                applied_on,
                status,
                resume_version or None,
                cover_letter_sent,
                responded_on,
                interviewed_on,
                notes or None,
                interview_data
            ))

            conn.commit()
            return redirect(url_for('applications_page'))

        cursor.execute("""
            SELECT
                jobs.job_id,
                jobs.job_title,
                companies.company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.company_id
            ORDER BY companies.company_name, jobs.job_title
        """)
        jobs = cursor.fetchall()

        return render_template(
            'add_application.html',
            jobs=jobs
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/applications/edit/<int:application_id>', methods=['GET', 'POST'])
def edit_application(application_id):
    from datetime import date, datetime

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM applications WHERE application_id = %s",
            (application_id,)
        )
        application = cursor.fetchone()

        if application is None:
            return "Application not found.", 404

        import json

        interview_details = application.get('interview_data')

        if isinstance(interview_details, (str, bytes)):
            interview_details = json.loads(interview_details)

        if not isinstance(interview_details, dict):
            interview_details = {}

        cursor.execute("""
            SELECT jobs.job_id, jobs.job_title, companies.company_name
            FROM jobs
            JOIN companies ON jobs.company_id = companies.company_id
            ORDER BY companies.company_name, jobs.job_title
        """)
        jobs = cursor.fetchall()

        if request.method == 'POST':
            job_id = request.form.get('job_id', '').strip()
            application_date = request.form.get(
                'application_date', ''
            ).strip()
            status = request.form.get('status', 'Applied').strip()
            resume_version = request.form.get(
                'resume_version', ''
            ).strip()
            cover_letter_sent = (
                1 if request.form.get('cover_letter_sent') == '1'
                else 0
            )
            response_date = request.form.get(
                'response_date', ''
            ).strip()
            interview_date = request.form.get(
                'interview_date', ''
            ).strip()
            notes = request.form.get('notes', '').strip()

            interview_type = request.form.get('interview_type', '').strip()
            interviewer = request.form.get('interviewer', '').strip()
            interview_location = request.form.get('interview_location', '').strip()
            interview_feedback = request.form.get('interview_feedback', '').strip()

            valid_interview_types = (
                '', 'Phone', 'Video', 'In Person',
                'Technical', 'Behavioral'
            )

            if interview_type not in valid_interview_types:
                return "Please select a valid interview type.", 400

            if len(interviewer) > 100 or len(interview_location) > 200:
                return "Interview details are too long.", 400

            updated_interview_details = {
                'interview_type': interview_type,
                'interviewer': interviewer,
                'location': interview_location,
                'feedback': interview_feedback
            }

            interview_data = (
                json.dumps(updated_interview_details)
                if any(updated_interview_details.values())
                else None
            )

            if not job_id.isdigit() or not any(
                job['job_id'] == int(job_id) for job in jobs
            ):
                return "Please select a valid job.", 400

            try:
                applied_on = date.fromisoformat(application_date)
                responded_on = (
                    date.fromisoformat(response_date)
                    if response_date else None
                )
                interviewed_on = (
                    datetime.fromisoformat(interview_date)
                    if interview_date else None
                )
            except ValueError:
                return "Please enter valid dates.", 400

            valid_statuses = (
                'Applied', 'Screening', 'Interview',
                'Offer', 'Rejected', 'Withdrawn'
            )

            if status not in valid_statuses:
                return "Please select a valid status.", 400

            if len(resume_version) > 50:
                return "Resume version is too long.", 400


            cursor.execute("""
                UPDATE applications
                SET job_id = %s,
                    application_date = %s,
                    status = %s,
                    resume_version = %s,
                    cover_letter_sent = %s,
                    response_date = %s,
                    interview_date = %s,
                    notes = %s,
                    interview_data = %s
                WHERE application_id = %s
            """, (
                int(job_id),
                applied_on,
                status,
                resume_version or None,
                cover_letter_sent,
                responded_on,
                interviewed_on,
                notes or None,
                interview_data,
                application_id
            ))

            conn.commit()
            return redirect(url_for('applications_page'))

        return render_template(
            'edit_application.html',
            application=application,
            jobs=jobs,
            interview_details=interview_details
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/applications/delete/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT application_id FROM applications WHERE application_id = %s",
            (application_id,)
        )

        application = cursor.fetchone()

        if application is None:
            return "Application not found.", 404

        cursor.execute(
            "DELETE FROM applications WHERE application_id = %s",
            (application_id,)
        )

        conn.commit()

        return redirect(url_for('applications_page'))

    finally:
        cursor.close()
        conn.close()

@app.route('/contacts')
def contacts_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                contacts.contact_id,
                contacts.first_name,
                contacts.last_name,
                companies.company_name,
                contacts.job_title,
                contacts.email,
                contacts.phone,
                contacts.linkedin_url,
                contacts.notes
            FROM contacts
            JOIN companies
                ON contacts.company_id = companies.company_id
            ORDER BY contacts.first_name, contacts.last_name
        """)

        contacts = cursor.fetchall()

        return render_template(
            'contacts.html',
            contacts=contacts
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'POST':
            company_id = request.form.get('company_id', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            job_title = request.form.get('job_title', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            notes = request.form.get('notes', '').strip()

            if not company_id.isdigit():
                return "Please select a valid company.", 400

            if not first_name or not last_name:
                return "First and last name are required.", 400

            if len(first_name) > 100 or len(last_name) > 100:
                return "Name is too long.", 400

            if (len(job_title) > 100 or len(email) > 255
                    or len(phone) > 30 or len(linkedin_url) > 500):
                return "One or more fields are too long.", 400

            cursor.execute(
                "SELECT company_id FROM companies WHERE company_id = %s",
                (int(company_id),)
            )

            if cursor.fetchone() is None:
                return "The selected company does not exist.", 400

            cursor.execute("""
                INSERT INTO contacts (
                    company_id, first_name, last_name,
                    job_title, email, phone, linkedin_url, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                int(company_id),
                first_name,
                last_name,
                job_title or None,
                email or None,
                phone or None,
                linkedin_url or None,
                notes or None
            ))

            conn.commit()
            return redirect(url_for('contacts_page'))

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)

        companies = cursor.fetchall()

        return render_template(
            'add_contact.html',
            companies=companies
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )
        contact = cursor.fetchone()

        if contact is None:
            return "Contact not found.", 404

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        companies = cursor.fetchall()

        if request.method == 'POST':
            company_id = request.form.get('company_id', '').strip()
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            job_title = request.form.get('job_title', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            linkedin_url = request.form.get('linkedin_url', '').strip()
            notes = request.form.get('notes', '').strip()

            if not company_id.isdigit() or not any(
                company['company_id'] == int(company_id)
                for company in companies
            ):
                return "Please select a valid company.", 400

            if not first_name or not last_name:
                return "First and last name are required.", 400

            if len(first_name) > 100 or len(last_name) > 100:
                return "Name is too long.", 400

            if (len(job_title) > 100 or len(email) > 255
                    or len(phone) > 30 or len(linkedin_url) > 500):
                return "One or more fields are too long.", 400

            cursor.execute("""
                UPDATE contacts
                SET company_id = %s,
                    first_name = %s,
                    last_name = %s,
                    job_title = %s,
                    email = %s,
                    phone = %s,
                    linkedin_url = %s,
                    notes = %s
                WHERE contact_id = %s
            """, (
                int(company_id),
                first_name,
                last_name,
                job_title or None,
                email or None,
                phone or None,
                linkedin_url or None,
                notes or None,
                contact_id
            ))

            conn.commit()
            return redirect(url_for('contacts_page'))

        return render_template(
            'edit_contact.html',
            contact=contact,
            companies=companies
        )

    finally:
        cursor.close()
        conn.close()

@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT contact_id FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )

        contact = cursor.fetchone()

        if contact is None:
            return "Contact not found.", 404

        cursor.execute(
            "DELETE FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )

        conn.commit()

        return redirect(url_for('contacts_page'))

    finally:
        cursor.close()
        conn.close()

@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    import json

    if request.method == 'GET':
        return render_template('job_match.html')

    skills_input = request.form.get('skills', '').strip()

    if not skills_input:
        return "Please enter at least one skill.", 400

    # converts entered skills into a lowercase set
    user_skills = {
        skill.strip().casefold()
        for skill in skills_input.split(',')
        if skill.strip()
    }

    if not user_skills:
        return "Please enter at least one valid skill.", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                jobs.job_id,
                jobs.job_title,
                jobs.requirements,
                companies.company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.company_id
            WHERE jobs.requirements IS NOT NULL
        """)

        jobs = cursor.fetchall()
        matches = []

        for job in jobs:
            requirements = job['requirements']

            # MySQL may return JSON as text
            if isinstance(requirements, (str, bytes)):
                requirements = json.loads(requirements)

            # only processes lists of skills
            if not isinstance(requirements, list):
                continue

            required_skills = [
                skill.strip()
                for skill in requirements
                if isinstance(skill, str) and skill.strip()
            ]

            if not required_skills:
                continue

            # removes duplicate skills ignoring capitalization
            unique_skills = list({
                skill.casefold(): skill
                for skill in required_skills
            }.values())

            matched_skills = [
                skill for skill in unique_skills
                if skill.casefold() in user_skills
            ]

            missing_skills = [
                skill for skill in unique_skills
                if skill.casefold() not in user_skills
            ]

            match_percentage = round(
                len(matched_skills) / len(unique_skills) * 100
            )

            matches.append({
                'job_title': job['job_title'],
                'company_name': job['company_name'],
                'match_percentage': match_percentage,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills
            })

        # only shows the highest matches first
        matches.sort(
            key=lambda match: match['match_percentage'],
            reverse=True
        )

        return render_template(
            'job_match.html',
            matches=matches,
            skills_input=skills_input
        )

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)