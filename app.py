from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import get_db, init_db
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Dashboard page with statistics"""
    conn = get_db()
    if conn is None:
        return "Database connection failed", 500

    cursor = conn.cursor(dictionary=True)

    # Get application statistics
    cursor.execute('SELECT COUNT(*) as total FROM applications')
    app_total = cursor.fetchone()['total']

    cursor.execute('''
        SELECT status, COUNT(*) as count FROM applications
        GROUP BY status
    ''')
    app_by_status = {row['status']: row['count'] for row in cursor.fetchall()}

    # Get contact statistics
    cursor.execute('SELECT COUNT(*) as total FROM contacts')
    contact_total = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as count FROM contacts WHERE email IS NOT NULL')
    contact_with_email = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM contacts WHERE phone IS NOT NULL')
    contact_with_phone = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM contacts WHERE linkedin_url IS NOT NULL')
    contact_with_linkedin = cursor.fetchone()['count']

    # Get job statistics
    cursor.execute('SELECT COUNT(*) as total FROM jobs')
    job_total = cursor.fetchone()['total']

    cursor.execute('''
        SELECT job_type, COUNT(*) as count FROM jobs
        GROUP BY job_type
    ''')
    job_by_type = {row['job_type']: row['count'] for row in cursor.fetchall()}

    cursor.execute('SELECT MIN(salary_min) as min_salary, MAX(salary_max) as max_salary, AVG((salary_min + salary_max)/2) as avg_salary FROM jobs')
    salary_stats = cursor.fetchone()

    # Get company statistics
    cursor.execute('SELECT COUNT(*) as total FROM companies')
    company_total = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as count FROM companies WHERE website IS NOT NULL')
    company_with_website = cursor.fetchone()['count']

    cursor.execute('SELECT DISTINCT industry FROM companies WHERE industry IS NOT NULL')
    industries = [row['industry'] for row in cursor.fetchall()]

    conn.close()

    stats = {
        'applications': {
            'total': app_total,
            'by_status': app_by_status
        },
        'contacts': {
            'total': contact_total,
            'with_email': contact_with_email,
            'with_phone': contact_with_phone,
            'with_linkedin': contact_with_linkedin
        },
        'jobs': {
            'total': job_total,
            'by_type': job_by_type,
            'salary': salary_stats
        },
        'companies': {
            'total': company_total,
            'with_website': company_with_website,
            'industries': industries
        }
    }

    return render_template('dashboard.html', stats=stats)

@app.route('/companies')
def companies():
    """List all companies"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM companies')
    companies_list = cursor.fetchall()
    conn.close()
    return render_template('companies.html', companies=companies_list)

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    """Add a new company"""
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO companies (company_name, industry, website, city, state, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (request.form['company_name'], request.form['industry'],
              request.form['website'], request.form['city'],
              request.form['state'], request.form['notes']))
        conn.commit()
        conn.close()
        return redirect(url_for('companies'))
    return render_template('company_form.html')

@app.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
def edit_company(id):
    """Edit a company"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute('''
            UPDATE companies SET company_name=%s, industry=%s, website=%s,
            city=%s, state=%s, notes=%s WHERE company_id=%s
        ''', (request.form['company_name'], request.form['industry'],
              request.form['website'], request.form['city'],
              request.form['state'], request.form['notes'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('companies'))

    cursor.execute('SELECT * FROM companies WHERE company_id=%s', (id,))
    company = cursor.fetchone()
    conn.close()
    return render_template('company_form.html', company=company)

@app.route('/companies/<int:id>/delete')
def delete_company(id):
    """Delete a company"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM companies WHERE company_id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('companies'))

@app.route('/jobs')
def jobs():
    """List all jobs"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT j.*, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    jobs_list = cursor.fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs_list)

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    """Add a new job"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Parse comma-separated requirements into a list
        requirements_str = request.form.get('requirements', '').strip()
        requirements = [req.strip() for req in requirements_str.split(',') if req.strip()] if requirements_str else []

        cursor.execute('''
            INSERT INTO jobs (company_id, job_title, job_type, salary_min,
            salary_max, job_url, date_posted, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (request.form['company_id'] if request.form['company_id'] else None,
              request.form['job_title'], request.form['job_type'],
              request.form['salary_min'] if request.form['salary_min'] else None,
              request.form['salary_max'] if request.form['salary_max'] else None,
              request.form['job_url'], request.form['date_posted'],
              json.dumps(requirements)))
        conn.commit()
        conn.close()
        return redirect(url_for('jobs'))

    cursor.execute('SELECT * FROM companies')
    companies_list = cursor.fetchall()
    conn.close()
    return render_template('job_form.html', companies=companies_list)

@app.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
def edit_job(id):
    """Edit a job"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Parse comma-separated requirements into a list
        requirements_str = request.form.get('requirements', '').strip()
        requirements = [req.strip() for req in requirements_str.split(',') if req.strip()] if requirements_str else []

        cursor.execute('''
            UPDATE jobs SET company_id=%s, job_title=%s, job_type=%s,
            salary_min=%s, salary_max=%s, job_url=%s, date_posted=%s,
            requirements=%s WHERE job_id=%s
        ''', (request.form['company_id'] if request.form['company_id'] else None,
              request.form['job_title'], request.form['job_type'],
              request.form['salary_min'] if request.form['salary_min'] else None,
              request.form['salary_max'] if request.form['salary_max'] else None,
              request.form['job_url'], request.form['date_posted'],
              json.dumps(requirements), id))
        conn.commit()
        conn.close()
        return redirect(url_for('jobs'))

    cursor.execute('SELECT * FROM jobs WHERE job_id=%s', (id,))
    job = cursor.fetchone()
    # Convert JSON requirements to comma-separated string for display
    if job and job['requirements']:
        try:
            reqs = json.loads(job['requirements'])
            job['requirements_display'] = ', '.join(reqs) if isinstance(reqs, list) else ''
        except:
            job['requirements_display'] = ''
    cursor.execute('SELECT * FROM companies')
    companies_list = cursor.fetchall()
    conn.close()
    return render_template('job_form.html', job=job, companies=companies_list)

@app.route('/jobs/<int:id>/delete')
def delete_job(id):
    """Delete a job"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE job_id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('jobs'))

@app.route('/applications')
def applications():
    """List all applications"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT a.*, j.job_title, c.company_name FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    apps_list = cursor.fetchall()
    conn.close()
    return render_template('applications.html', applications=apps_list)

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    """Add a new application"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            interview_data = json.loads(request.form.get('interview_data', '{}'))
        except:
            interview_data = {}

        cursor.execute('''
            INSERT INTO applications (job_id, application_date, status,
            resume_version, cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (request.form['job_id'], request.form['application_date'],
              request.form['status'], request.form['resume_version'],
              request.form.get('cover_letter_sent') == 'on',
              json.dumps(interview_data)))
        conn.commit()
        conn.close()
        return redirect(url_for('applications'))

    cursor.execute('''
        SELECT j.job_id, j.job_title, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    jobs_list = cursor.fetchall()
    conn.close()
    return render_template('application_form.html', jobs=jobs_list)

@app.route('/applications/<int:id>/edit', methods=['GET', 'POST'])
def edit_application(id):
    """Edit an application"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            interview_data = json.loads(request.form.get('interview_data', '{}'))
        except:
            interview_data = {}

        cursor.execute('''
            UPDATE applications SET job_id=%s, application_date=%s, status=%s,
            resume_version=%s, cover_letter_sent=%s, interview_data=%s
            WHERE application_id=%s
        ''', (request.form['job_id'], request.form['application_date'],
              request.form['status'], request.form['resume_version'],
              request.form.get('cover_letter_sent') == 'on',
              json.dumps(interview_data), id))
        conn.commit()
        conn.close()
        return redirect(url_for('applications'))

    cursor.execute('SELECT * FROM applications WHERE application_id=%s', (id,))
    application = cursor.fetchone()
    cursor.execute('''
        SELECT j.job_id, j.job_title, c.company_name FROM jobs j
        LEFT JOIN companies c ON j.company_id = c.company_id
    ''')
    jobs_list = cursor.fetchall()
    conn.close()
    return render_template('application_form.html', application=application, jobs=jobs_list)

@app.route('/applications/<int:id>/delete')
def delete_application(id):
    """Delete an application"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE application_id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('applications'))

@app.route('/contacts')
def contacts():
    """List all contacts"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT c.*, co.company_name FROM contacts c
        LEFT JOIN companies co ON c.company_id = co.company_id
    ''')
    contacts_list = cursor.fetchall()
    conn.close()
    return render_template('contacts.html', contacts=contacts_list)

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    """Add a new contact"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute('''
            INSERT INTO contacts (company_id, contact_name, title, email,
            phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (request.form['company_id'] if request.form['company_id'] else None,
              request.form['contact_name'], request.form['title'],
              request.form['email'], request.form['phone'],
              request.form['linkedin_url'], request.form['notes']))
        conn.commit()
        conn.close()
        return redirect(url_for('contacts'))

    cursor.execute('SELECT * FROM companies')
    companies_list = cursor.fetchall()
    conn.close()
    return render_template('contact_form.html', companies=companies_list)

@app.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
def edit_contact(id):
    """Edit a contact"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        cursor.execute('''
            UPDATE contacts SET company_id=%s, contact_name=%s, title=%s,
            email=%s, phone=%s, linkedin_url=%s, notes=%s WHERE contact_id=%s
        ''', (request.form['company_id'] if request.form['company_id'] else None,
              request.form['contact_name'], request.form['title'],
              request.form['email'], request.form['phone'],
              request.form['linkedin_url'], request.form['notes'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('contacts'))

    cursor.execute('SELECT * FROM contacts WHERE contact_id=%s', (id,))
    contact = cursor.fetchone()
    cursor.execute('SELECT * FROM companies')
    companies_list = cursor.fetchall()
    conn.close()
    return render_template('contact_form.html', contact=contact, companies=companies_list)

@app.route('/contacts/<int:id>/delete')
def delete_contact(id):
    """Delete a contact"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE contact_id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('contacts'))

@app.route('/job-match')
def job_match():
    """Job matching page based on skills"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    search_query = request.args.get('search', '')
    matched_jobs = []

    if search_query:
        # Get all jobs and match based on skills
        cursor.execute('SELECT * FROM jobs')
        jobs_list = cursor.fetchall()

        search_skills = set(s.strip().lower() for s in search_query.split(','))

        for job in jobs_list:
            if job['requirements']:
                try:
                    job_requirements = json.loads(job['requirements'])
                    if isinstance(job_requirements, list):
                        job_skills = set(s.lower() for s in job_requirements)
                    else:
                        job_skills = set()
                except:
                    job_skills = set()
            else:
                job_skills = set()

            if job_skills and search_skills:
                match_percentage = (len(search_skills & job_skills) / len(job_skills)) * 100
                job['match_percentage'] = round(match_percentage)
                matched_jobs.append(job)

        # Sort by match percentage
        matched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)

    conn.close()
    return render_template('job_match.html', jobs=matched_jobs, search_query=search_query)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
