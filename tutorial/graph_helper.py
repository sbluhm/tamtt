# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from datetime import datetime, timedelta

# <FirstCodeSnippet>
from requests_oauthlib import OAuth2Session

#graph_url = 'https://graph.microsoft.com/v1.0'
graph_url = 'https://graph.microsoft.com/beta'

def get_user(token):
  graph_client = OAuth2Session(token=token)
  # Send GET to /me
  user = graph_client.get('{0}/me'.format(graph_url))
  # Return the JSON result
  return user.json()
# </FirstCodeSnippet>

# <GetPresenceSnippet>
def get_presence_events(token):
  graph_client = OAuth2Session(token=token)
  presence = graph_client.get('{0}/me/presence'.format(graph_url))
  # Return the JSON result
  return presence.json()

# </GetPresenceSnippet>

# <GetCalendarSnippet>
# input_week is an ISO date of one of the days within the considered week.
def get_calendar_events(token, input_week=datetime.now().strftime("%Y-%m-%d")):
  graph_client = OAuth2Session(token=token)

  # Get saturday on/before given date
  #TODO: Time zones are not considered! (who cares about others...)
  week = datetime.strptime(input_week, "%Y-%m-%d")
  start_date = week - timedelta(days=week.weekday()+2) # Saturday before input_week
  end_date = start_date + timedelta(days=6)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,start,end,categories',
    '$orderby': 'start/DateTime DESC',
    '$top': 500,
    '$filter': "showAs eq 'busy'"
  }

# Send GET to /me/calendar
  events = graph_client.get('{0}/me/calendar/calendarView?startDateTime={1}T00:00:00&endDateTime={2}T23:59:59'.format(graph_url,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d")), params=query_params)
  # Return the JSON result
  return events.json()
# </GetCalendarSnippet>
