# Calen - SPOC 1:1 Connect Meeting Scheduler

## Purpose
This repository contains the code for the SPOC Meeting Connect project. The project is a proof of concept for booking 1:1 meetings on Google Calendar with many Team members in the org.

## Requirements
* Python
* Google Calendar API
* Google Account

## Setup
* Clone the repo
* Create a Google Cloud Platform project & Enable the Google Calendar API
* Make sure that your user has API Access to perform Google Calendar API calls
* Download the credentials.json file & place it in the root of the project
* Create a virtual environment & Install the requirements
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- export the environment variables as given below
- `python3 main.py`
* The script will open a link in the browser
* Select the Google account that you want to use to create the events & Allow the permissions
* The script will run and create the event on the Google Calendar
* The script will print the event details if scheduled successfully

## Environment Variables
export following variables for configuring the script

```bash
export ORGANIZER_EMAIL="nihitjain11@gmail.com"
export SPOC_EMAILS=['fury@shield.com'] #[list of emails]
export ATTENDEES_EMAILS_LIST=['steve@avengers.com','romanoff@avengers.com','tony@avengers.com','hulk@avengers.com','thor@avengers.com','strange@avengers.com'] # [list of emails]

export SEND_NOTIFICATIONS=True #False

export DESCRIPTION="""<h3>Monthly meet-up with Avengers</h3>
- Current Mission Status
- Change in Roles & responsibilities
- Contributions to the local community
- Any upcoming threats/missions
- Engagement & Availability
- Any feedback
- Accompanying member(s)
"""

export TIMEZONE='IST' #timezone
export TZ="+05:30" #timezone offset from UTC
export YEAR=2023
export MONTH=10

#### define specific dates 
export DATES=[11,18,25] # [list of integer dates]

export START_TIME=15 # 3pm or 15th hour in 24 hour format
export STEP_TIME=10 # meeting duration in minutes 
export END_TIME=17 # 5pm or 17th hour in 24 hour format
```