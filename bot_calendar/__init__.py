from __future__ import print_function

import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'prtpb6825s7lke9gfsharj0dhg@group.calendar.google.com'
BOT_SERVICE_ID = 'bot-213@botshed.iam.gserviceaccount.com'
SERVICE_ACCOUNT_FILE = 'bot_cred.json'
SLOT_SIZE_MIN = 15


def set_event(order):
    # setting service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    message_text = order.name + " " + order.phone
    # dat=order.date.strftime("%Y-%M-%D")
    start = datetime.datetime(order.date.year, order.date.month, order.date.day, int(order.hours), int(order.minutes),
                              00, 000000)
    end = start + datetime.timedelta(minutes=SLOT_SIZE_MIN)
    # dat =dat +"T"+order.hours+":"+order.minutes+":00+03:00"

    event = {
        'summary': message_text,

        'start': {
            'dateTime': start.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },
        'end': {
            'dateTime': end.isoformat(),
            'timeZone': 'Asia/Jerusalem'
        },

    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)

    s = service.calendars().get(calendarId='botshed.test@gmail.com')

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def get_empty_slots_for_day(date):
    try:

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        service = build('calendar', 'v3', credentials=creds)

        now = date.isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting all events for today')
        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    except Exception as e:
        print(e)


if __name__ == '__main__':
    now = datetime.datetime.now()
    get_empty_slots_for_day(now)
