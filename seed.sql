USE job_tracker;

-- sample company for demonstration
INSERT INTO companies
(company_name, industry, website, city, state, notes)
SELECT
    'Demo Tech Solutions',
    'Technology',
    'https://example.com',
    'Miami',
    'FL',
    'Fictional company for project demonstration'
WHERE NOT EXISTS (
    SELECT 1
    FROM companies
    WHERE company_name = 'Demo Tech Solutions'
);

-- sample job for demonstration
INSERT INTO jobs
(company_id, job_title, job_description,
 salary_min, salary_max, job_type, date_posted,
 requirements)
SELECT
    c.company_id,
    'Cybersecurity Analyst Intern',
    'Assist with security monitoring and incident response.',
    45000,
    60000,
    'Internship',
    '2026-11-01',
    JSON_OBJECT(
        'skills', JSON_ARRAY('Python', 'SQL', 'Networking'),
        'experience', 'Entry Level',
        'education', 'Computer Science or related field'
    )
FROM companies c
WHERE c.company_name = 'Demo Tech Solutions'
  AND NOT EXISTS (
      SELECT 1
      FROM jobs j
      WHERE j.company_id = c.company_id
        AND j.job_title = 'Cybersecurity Analyst Intern'
  )
ORDER BY c.company_id DESC
LIMIT 1;

-- sample application for demonstration
INSERT INTO applications
(job_id, application_date, status,
 resume_version, cover_letter_sent, notes, interview_data)
SELECT
    j.job_id,
    '2026-11-05',
    'Interview',
    'Cybersecurity Resume',
    1,
    'Applied for the cybersecurity internship.',
    JSON_OBJECT(
        'interview_type', 'Virtual',
        'interview_round', 1,
        'interview_notes',
        'Discuss Python, SQL, and networking skills'
    )
FROM jobs j
JOIN companies c
    ON j.company_id = c.company_id
WHERE c.company_name = 'Demo Tech Solutions'
  AND j.job_title = 'Cybersecurity Analyst Intern'
  AND NOT EXISTS (
      SELECT 1
      FROM applications a
      WHERE a.job_id = j.job_id
        AND a.application_date = '2026-11-05'
        AND a.resume_version = 'Cybersecurity Resume'
  )
ORDER BY j.job_id DESC
LIMIT 1;

-- sample contact for demonstration
INSERT INTO contacts
(company_id, first_name, last_name,
 email, job_title, notes)
SELECT
    c.company_id,
    'Sarah',
    'Johnson',
    'sarah.johnson@example.com',
    'Technical Recruiter',
    'Fictional recruiter for project demonstration'
FROM companies c
WHERE c.company_name = 'Demo Tech Solutions'
  AND NOT EXISTS (
      SELECT 1
      FROM contacts ct
      WHERE ct.company_id = c.company_id
        AND ct.email = 'sarah.johnson@example.com'
  )
ORDER BY c.company_id DESC
LIMIT 1;