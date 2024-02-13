from __future__ import print_function

import datetime
import os.path
import re
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

ORGANIZER_EMAIL = os.getenv("ORGANIZER_EMAIL")
SPOC_EMAILS = [ORGANIZER_EMAIL] + os.getenv("SPOC_EMAILS").strip('][').split(',') #co-hosts

ATTENDEES_EMAILS_LIST = os.getenv("ATTENDEES_EMAILS_LIST").strip('][').split(',')

UNSCHEDULED_ATTENDEES = []
SEND_NOTIFICATIONS = eval(os.getenv("SEND_NOTIFICATIONS"))

DESCRIPTION = os.getenv("DESCRIPTION")

TIMEZONE = os.getenv('TIMEZONE') #timezone
TZ = os.getenv('TZ') #timezone offset from UTC
YEAR = int(os.getenv('YEAR')) #year
MONTH = int(os.getenv('MONTH')) #month

#* define specific dates 
#! setting this will skip step(difference) based date range
DATES = os.getenv("DATES").strip('][').split(',')

#* define date by step(difference between days)
START_DATE = 1
STEP_DATE = 1
END_DATE = 31

START_TIME = int(int(os.getenv('START_TIME'))*60) #in minutes
STEP_TIME = int(os.getenv('STEP_TIME')) #in minutes
END_TIME = int(int(os.getenv('END_TIME'))*60) #in minutes

EVENTS = {}

def generate_timestamps():
    print("\ngenerating timestamps...")
    timestamps = []
    date_range = DATES if DATES else range(START_DATE,END_DATE+1,STEP_DATE)
    for DATE in date_range:
        for TIME in range(START_TIME,END_TIME,STEP_TIME):
            start = datetime.datetime.now().replace(day=int(DATE), month=MONTH, hour=TIME//60, minute=TIME%60, second=0)
            end = start + datetime.timedelta(minutes=STEP_TIME)

            timestamps.append([start.isoformat(timespec='seconds')+TZ,end.isoformat(timespec='seconds')+TZ])
    # print(timestamps)
    return timestamps

def check_availability(service, email, timestamps):
    print(f"checking availability with {email}...")
    AVAILABLE = None
    for TIME in timestamps:
        AVAILABLE = True
        attendees = [email] + SPOC_EMAILS
        
        # Check if the people in the list have time available for the meeting
        free_busy_times = service.freebusy().query(body={
            "timeMin": TIME[0],
            "timeMax": TIME[1],
            "timeZone": TIMEZONE,
            "items": [{"id": email} for email in attendees]
        }).execute()

        # print(free_busy_times)

        # Raise an error if any of the people in the list do not have time available for the meeting
        for attendee, calendar in free_busy_times["calendars"].items():
            if calendar.get("errors"):
                raise ValueError(calendar.get("errors")) # print if any errors

            if calendar.get("busy"):
                # print(f"{attendee} unavailable at {TIME[0]}")
                AVAILABLE = False
                break
        
        if AVAILABLE:
            # print(f"{email} is available at {TIME[0]}")
            AVAILABLE = TIME
            break

    if AVAILABLE == False:
        print (f"\nUnable to schedule meeting, at least one of the attendess is unavailable for the meeting!")
    else:
        print(f"\nMeeting available with {email} at {AVAILABLE[0]}.") 
    
    return AVAILABLE


def schedule(service, email, availability):
    name =  " ".join(((re.sub(r'\d+', '', email)).split('@')[0]).split('.')).title()
    event = {
        "summary": name + " | Americas BU - DevOps SPOC Monthly Connect",
        "start": {"dateTime": availability[0]},
        "end": {"dateTime": availability[1]},
        "attendees": [{"email" : id, "responseStatus" : "accepted" if id == ORGANIZER_EMAIL else "needsAction"} for id in [email] + SPOC_EMAILS],
        "conferenceData" : {
            "createRequest" : {
                "requestId" : name,
                "conferenceSolutionKey" : {"type" : "hangoutsMeet"}
            }
        },
        "description" : DESCRIPTION
    }
    # print(event)
    # input()
    
    schedule_event = service.events().insert(calendarId="primary", body=event, sendNotifications=SEND_NOTIFICATIONS, conferenceDataVersion=1).execute()
    
    # print(schedule_event)

    # print(f"Meeting with {email} scheduled for {event['start']}")
    
    return f"Scheduled! {event['summary']} at {event['start']} with {event['attendees']}"

def reschedule():
    #TODO 
    # add ability to reschedule events
    pass


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("Authenticated Successfully!")

    try:
        service = build('calendar', 'v3', credentials=creds)

        for email in ATTENDEES_EMAILS_LIST:
            availability = check_availability(service, email, generate_timestamps())
            if type(availability) is list:
                schedule_event = schedule(service, email, availability)
                print(schedule_event)

    except HttpError as error:
        print(f"\nAn error occurred: {error}\n")



if __name__ == '__main__':
    main()
