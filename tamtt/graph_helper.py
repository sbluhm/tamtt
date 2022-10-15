from datetime import datetime, timedelta
import json
import yaml

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
  print(presence)
  return presence.json()

# </GetPresenceSnippet>

# <GetCalendarSnippet>
# input_week is an ISO date of one of the days within the considered week.
def get_calendar_events(token, input_date=datetime.now().strftime("%Y-%m-%d")):
  graph_client = OAuth2Session(token=token)

  # Get saturday on/before given date
  #TODO: Time zones are not considered! (who cares about others...)
  week = datetime.strptime(input_date, "%Y-%m-%d")
  weekday = week.weekday()
  start_date = week - timedelta(days=week.weekday()+2) # Saturday before input_week
  if week.weekday() >= 5:
      start_date = start_date + timedelta(days=7)
  end_date = start_date + timedelta(days=6)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,start,end,categories,responseStatus,body,attendees,seriesMasterId',
    '$orderby': 'start/DateTime DESC',
    '$top': 500,
    '$filter': "showAs eq 'busy'"
  }

# Send GET to /me/calendar
  events = graph_client.get('{0}/me/calendar/calendarView?startDateTime={1}T00:00:00&endDateTime={2}T23:59:59'.format(graph_url,start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d")), params=query_params)
  # Return the JSON result
  return events.json()
# </GetCalendarSnippet>

# Function to update categories/tags based on event id
def patch_event_categories(token, event_id, categories=None):
  graph_client = OAuth2Session(token=token)

  # Set headers
  headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
  }
  print("Adding payload")
  payload= '{ "categories":' + json.dumps(categories) + ' }'
  updated_event = graph_client.patch('{0}/me/events/{1}'.format(graph_url, event_id), payload, headers=headers )
  return updated_event


# Funtion to read or create autotag config
def load_autotag_config(token):
  graph_client = OAuth2Session(token=token)

  request = graph_client.get('{0}/me/drive/special/approot:/autotag_config.yaml:/content'.format(graph_url))
  # Create config file if it is not already there. Ideally a message should be displayed.
  if request.status_code == 404:
    # TODO Prepopulate with documented sample file from server
    # Set headers
    headers = {
      'Authorization': f'Bearer {token}',
      'Content-Type': 'application/text'
    }

    request = graph_client.put('{0}/me/drive/special/approot:/autotag_config.yaml:/content'.format(graph_url), "", headers=headers)
    return

  config = yaml.safe_load(request.content)
  return config
