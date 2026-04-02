# Technical Requirements
This project was tested on Python3.14<br>
Ensure you run the following command before running the application:<br>
pip install -r requirements.txt<br>
<br>
Ensure you create a .env file within the roof folder and include the following fields:<br>
DATABASE_PASSWORD =<br> 
DB_HOST = <br>
DB_USER = <br>
DB_NAME = <br>

Defaults are usually:<br>
DATABASE_PASSWORD = There are no default passwords!<br>
DB_HOST = localhost<br>
DB_USER = root<br>
DB_NAME = job_tracker<br>
<br>
Afterwards, run the application with the following command:<br>
py app.py

# Design Overview

## Dashboard Page
Dashboard contains statistics about various subjects. User can click on drop down under the subject to reveal statistics regarding that subject.
The details are as follows:
#### Applications
Total number of applications, total number of applications under specific a status (Applied, Screening, Interview, Offer, Rejected, Withdrawn)

#### Contacts
Total number of contacts, contacts with emails, contacts with phone numbers, contacts with linkedin's

#### Jobs
Total Jobs, total jobs within type categories (Full time, Part-time, Contract, Internship)

#### Companies
Total Companies, Total websites, List of all industries

## Job Match Page
Determines potential jobs based on skills. Users can search for skills and select them. Then, the site returns matching jobs based on percentage of skills the user matches with the job.

## Companies Page
Shows a list of all companies, including options to edit and delete them. Page also features a button to add a new company.

## Jobs Page 
Same as companies page, however, instead of companies, with jobs.

## Applications Page
Same as companies page, however, instead of companies, with applications.

## Contacts Page
Same as companies page, however, instead of companies, with contacts

