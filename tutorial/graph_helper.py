# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

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
def get_calendar_events(token):
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,start,end,categories',
    '$orderby': 'start/DateTime DESC',
    '$top': 500,
    '$filter': "showAs eq 'busy'"
  }
# $filter=start/dateTime ge '2021-04-21T00:00' and end/dateTime lt '2021-04-22T00:00'&$select=subject,start,end,categories"

  # Send GET to /me/events
#  events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
  events = graph_client.get('{0}/me/calendar/calendarView?startDateTime=2021-04-10T00:00:00&endDateTime=2021-04-16T23:59:59'.format(graph_url), params=query_params)
  # Return the JSON result
  return events.json()
# </GetCalendarSnippet>
