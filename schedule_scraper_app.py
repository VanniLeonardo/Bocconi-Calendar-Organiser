from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import datetime
from constants import LECTURES_ID, EXAMS_ID, REGEX_DICT, CLASSES, MAX_RESULTS
import re
import pytz

#Grant Read/Write access to the calendar
#for read-only access use 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    # Authenticate the user
    credentials = authenticate_user()
    
    # Build the service
    service = build('calendar', 'v3', credentials=credentials)

    # Scrape the calendar for the lecture schedule
    events = scrape_calendar(service=service, calendar_id=LECTURES_ID, max_results=MAX_RESULTS)

    if not events:
        print('No upcoming Lectures found.')
        return None

    to_create_events = []

    for event in events:
        # Scrape the time from description and convert to local time
        start = UTC_to_local(event['start']['dateTime'], 'Europe/Rome')
        end = UTC_to_local(event['end']['dateTime'], 'Europe/Rome')
        
        summary = event.get('summary', '')
        description = event.get('description', '')

        temp_event = {}
        temp_event['code'] = summary[:5]
        temp_event['start'] = start.strftime('%H:%M')
        temp_event['end'] = end.strftime('%H:%M')
        temp_event['date'] = start.strftime('%d/%m/%Y')
        temp_event['location'] = 'Online'
        temp_event['color'] = 'blue'


        # Check if "in presenza" or "on campus" is in the summary
        if re.search(r'in presenza', summary, re.IGNORECASE) or re.search(r'on campus', summary, re.IGNORECASE):
            temp_event['location'] = re.search(r'Aula (\d+)', summary).group(1)
            temp_event['color'] = 'yellow'
        
        # Determine which of the specified words are in the description
        for keyword in CLASSES:
            if re.search(fr'\b{keyword}\b', description, re.IGNORECASE):
                temp_event['course'] = REGEX_DICT[keyword]
        print(temp_event)
        # Add the event to the list of events to create
        to_create_events.append(temp_event)

    # Create a new calendar for the lectures
    lectures_calendar_id = create_lectures_calendar(service)

    # Create the events in the new calendar
    for event in to_create_events:
        create_event(service, lectures_calendar_id, event)


def authenticate_user():
    '''Authenticate the user using the Google Calendar API to have read/write access to the calendar'''
    credentials = None

    # Store user's access and refresh tokens in token.pickle
    # If user already authenticated, load credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        # If the credentials are expired, refresh them
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        # If the credentials are not found, create them
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def scrape_calendar(service, calendar_id, max_results, start=datetime.datetime.utcnow().isoformat() + 'Z'):
    '''Scrape the given calendar for the max_results number of events starting from time start'''
    events_result = service.events().list(calendarId=calendar_id, timeMin=start,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def UTC_to_local(utc_datetime, timezone):
    '''Convert a UTC datetime to the specified timezone'''
    utc_datetime = datetime.datetime.fromisoformat(utc_datetime.replace('Z', '+00:00'))
    local_tz = pytz.timezone(timezone)
    local_datetime = utc_datetime.astimezone(local_tz)
    return local_datetime

def scrape_times(description):
    '''Scrape the start and end times of the lecture from the description'''
    # Use regex to capture start and end times in the format HH:MM - HH:MM
    match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', description)
    if match:
        start_time, end_time = match.groups()
        return start_time, end_time
    return None, None

def create_lectures_calendar(service):
    '''Create a new calendar for the lectures if it does not already exist'''
    # List all calendars
    calendars = service.calendarList().list().execute()
    
    # Check if a calendar with the name "Lectures" already exists
    for calendar in calendars['items']:
        if calendar['summary'] == 'Lectures':
            print(f"Found existing calendar with ID: {calendar['id']}")
            return calendar['id']
    
    # If no existing calendar found, create a new one
    calendar = {
        'summary': 'Lectures',
        'timeZone': 'Europe/Rome'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    print(f"Created calendar with ID: {created_calendar['id']}")
    return created_calendar['id']


def create_event(service, calendar_id, event_data):
    '''Create an event in the specified calendar with the given data'''
    # Construct the event
    event = {
        'summary': event_data['course'],
        'location': 'Classroom ' + event_data['location'],
        'description': f"{event_data['code']} {event_data['course']} in classroom {event_data['location']}",
        'start': {
            'dateTime': datetime.datetime.strptime(f"{event_data['date']} {event_data['start']}", "%d/%m/%Y %H:%M").isoformat(),
            'timeZone': 'Europe/Rome',
        },
        'end': {
            'dateTime': (datetime.datetime.strptime(f"{event_data['date']} {event_data['end']}", "%d/%m/%Y %H:%M")).isoformat(),
            'timeZone': 'Europe/Rome',
        },
    }

    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Event created: {created_event.get('htmlLink')}")
    return created_event

if __name__ == '__main__':
    main()
