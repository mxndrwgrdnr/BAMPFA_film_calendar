import requests
from lxml import html
import lxml
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import argparse
import httplib2
from datetime import datetime, timedelta
import re

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret_254466080681-' \
    + 'liol8nsgiko02e8n48el5euov2mlpjuk.apps.googleusercontent.com.json'
APPLICATION_NAME = 'BAMPFA Calendar Scraper'
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
base_url = '''http://www.bampfa.berkeley.edu'''


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'bampfa-calendar-scraper.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return credentials


def post_event(event_id, title, description, start_dttm, end_dttm):
    """Posts film screening to BAMPFA calendar.

    If event already exists, it is skipped.

    Returns:
        None
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    cal_id = 'q8cvu1a9sn3f1l33f6s3915618@group.calendar.google.com'

    event = {
        'id': event_id,
        'summary': title,
        'location': 'BAMPFA',
        'description': description,
        'start': {
            'dateTime': start_dttm,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_dttm,
            'timeZone': 'America/Los_Angeles',
        },
        'reminders': {
            'useDefault': True
        },
    }
    try:
        service.events().get(calendarId=cal_id, eventId=event_id).execute()
        print 'dupe'
    except:
        event = service.events(). \
            insert(calendarId=cal_id, body=event).execute()
        print 'Event created: %s' % (event.get('htmlLink'))


def scrape_6_mos(calendar, session):
    """Gets 6 months of films from the BAMPFA film calendar.

    The current month's calendar is passed as a function
    argument. The function then loops through the next 5
    calendar months and appends the results of each month
    to the list Films.

    Returns:
        List of tuples with info for each film screening.
    """

    s = session
    films = []
    tree = html.fromstring(calendar.content.decode(calendar.encoding))
    for i in range(6):
        days = tree.xpath("//tr[@class='single-day']/td")
        for day in days:
            date = day.xpath("@data-date")[0]
            events = day.xpath(".//div[@class='popupboxthing']/div" +
                               "[@class='views-row']" +
                               "/div[@class='calendar-event']")
            if len(events) > 0:
                for event in events:
                    event_id = events[0].xpath("../../@data-popup")[0]
                    time_str = event.xpath(
                        ".//div[@class='time']//strong/text()")[0]
                    if type(time_str) == lxml.etree._ElementUnicodeResult:
                        continue
                    if ':' in time_str:
                        timestamp = datetime.strptime(date + ' ' + time_str,
                                                      '%Y-%m-%d %I:%M %p')
                    else:
                        timestamp = datetime.strptime(date + ' ' + time_str,
                                                      '%Y-%m-%d %I %p')
                    st_ts = timestamp.isoformat()
                    end_ts = (timestamp + timedelta(hours=2)).isoformat()
                    event_id = 'id' + event_id + 'ts' + \
                        timestamp.strftime('%s')
                    info = event.xpath(".//div[@class='event-content']")[0]
                    title = info.xpath("div[@class='title']/a/text()")[0]
                    rel_url = info.xpath("div[@class='title']/a/@href")[0]
                    full_url = base_url + rel_url
                    details = info.xpath("div[@class='cb_details']/div/text()")
                    details_wo_nl = re.split(r"\n[ ]{2,}|[ ]{2,}",
                                             ','.join(details))
                    details_wo_comm = re.split(
                        r",{2,}", ','.join(details_wo_nl))
                    clean_details = ', '.join(details_wo_comm). \
                        rstrip(',').lstrip(',')
                    summary = info.xpath(
                        "div[@class='event-summary']/text()")[0]. \
                        lstrip('\n ').rstrip('\n ')
                    description = clean_details + '\n' + summary + \
                        '\n' + full_url
                    films.append((event_id, title, description, st_ts, end_ts))
        next_month_url = tree.xpath(
            "//span[@class='pager next']/a/@href")[0].replace('[0]', '%5B%5D')
        next_month_cal = s.get(next_month_url)
        tree = html.fromstring(
            next_month_cal.content.decode(next_month_cal.encoding))

    return films


def main():
    s = requests.Session()
    cur_month_cal = s.get(
        base_url + "/visit/calendar?calendar_filter%5B%5D=47490")
    films = scrape_6_mos(cur_month_cal, s)
    for film in films:
        post_event(*film)


if __name__ == '__main__':
    main()
