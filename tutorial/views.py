# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tutorial.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from tutorial.graph_helper import get_user, get_calendar_events, get_presence_events
import dateutil.parser
import datetime

# <HomeViewSnippet>
def home(request):
  context = initialize_context(request)

  return render(request, 'tutorial/home.html', context)
# </HomeViewSnippet>

# <InitializeContextSnippet>
def initialize_context(request):
  context = {}

  # Check for any errors in the session
  error = request.session.pop('flash_error', None)

  if error != None:
    context['errors'] = []
    context['errors'].append(error)

  # Check for user in the session
  context['user'] = request.session.get('user', {'is_authenticated': False})
  return context
# </InitializeContextSnippet>

# <SignInViewSnippet>
def sign_in(request):
  # Get the sign-in URL
  sign_in_url, state = get_sign_in_url()
  # Save the expected state so we can validate in the callback
  request.session['auth_state'] = state
  # Redirect to the Azure sign-in page
  return HttpResponseRedirect(sign_in_url)
# </SignInViewSnippet>

# <SignOutViewSnippet>
def sign_out(request):
  # Clear out the user and token
  remove_user_and_token(request)

  return HttpResponseRedirect(reverse('home'))
# </SignOutViewSnippet>

# <CallbackViewSnippet>
def callback(request):
  # Get the state saved in session
  expected_state = request.session.pop('auth_state', '')
  # Make the token request
  token = get_token_from_code(request.get_full_path(), expected_state)

  # Get the user's profile
  user = get_user(token)

  # Save token and user
  store_token(request, token)
  store_user(request, user)

  return HttpResponseRedirect(reverse('home'))
# </CallbackViewSnippet>


# <CalendarViewSnippet>
def calendar(request):
  context = initialize_context(request)

  token = get_token(request)

  events = get_calendar_events(token)
  timesheet = {}
  newtimesheet = {}


  if events:
    # Step one, split out and merge customers and deliverables
    for event in events['value']:
        temp_deliverable = {}
        temp_deliverable[ dateutil.parser.parse(event['start']['dateTime']).weekday() ] = dateutil.parser.parse(event['end']['dateTime']) - dateutil.parser.parse(event['start']['dateTime'] )
        if event['categories']:
            tempcust = []
            for category in event['categories']:
                if category[0].isdigit():
                    # here multiple deliverables should be allowed! Otherwise last deliverable is taken
                    temp_deliverable['category'] = category
                else:
                    tempcust.append(category)
            if not 'category' in temp_deliverable:
                temp_deliverable['category'] = "Others"
            for customer in tempcust:

                if not customer in newtimesheet:
                    newtimesheet[customer] = []
                    x_deliverable = {}
                    timesheet[customer] = x_deliverable
                # add to existing deliverables here
                if not temp_deliverable['category'] in timesheet[customer]:
                    day = [datetime.timedelta(0)]*7
                    timesheet[customer][temp_deliverable['category']] = day
                duration = dateutil.parser.parse(event['end']['dateTime']) - dateutil.parser.parse(event['start']['dateTime'] )
#                old = timesheet[customer][temp_deliverable['category']][0]
#                print(type(old))

#                timesheet[customer][temp_deliverable['category']][dateutil.parser.parse(event['start']['dateTime']).weekday() ] +=  dateutil.parser.parse(event['end']['dateTime']) #- dateutil.parser.parse(event['start']['dateTime'] ) 
                timesheet[customer][temp_deliverable['category']][dateutil.parser.parse(event['start']['dateTime']).weekday()] += duration

                for deliverable in newtimesheet[customer]:
                    for entry in deliverable['category']:
                        entry
                #Original line below
                newtimesheet[customer].append(temp_deliverable)
        else:
            temp_deliverable['category'] = "Others"

#            newtimesheet["Others"].append(deliverables)


    context['customer'] = timesheet



  return render(request, 'tutorial/calendar.html', context)
# </CalendarViewSnippet>

# <PresenceViewSnippet>
def presence(request):
  context = initialize_context(request)

  token = get_token(request)

  events = get_presence_events(token)

#  if events:
    # Convert the ISO 8601 date times to a datetime object
    # This allows the Django template to format the value nicely
#    for event in events['value']:
#      event['start']['dateTime'] = dateutil.parser.parse(event['start']['dateTime'])
#      event['end']['dateTime'] = dateutil.parser.parse(event['end']['dateTime'])
#
  context['events'] = events

  return render(request, 'tutorial/presence.html', context)
# </PresenceViewSnippet>
