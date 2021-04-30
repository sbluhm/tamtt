#TODO: Sort categories alphabetically.
#TODO: Handle parallel meetings sensibly.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tutorial.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from tutorial.graph_helper import get_user, get_calendar_events, get_presence_events
import dateutil.parser
from datetime import datetime, timedelta
from math import ceil

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
  preparation_time = timedelta(minutes=10)
  context = initialize_context(request)

  token = get_token(request)
  if request.GET.get('week'):
    selected_date = request.GET['week']
    events = get_calendar_events(token, selected_date)
  else:
    events = get_calendar_events(token)
    selected_date = datetime.now().strftime("%Y-%m-%d")


  timesheet = {}
  totaltime = [timedelta(0)]*8 # 8 will be the week total
  week_totaltime = timedelta(0)

  if events:
    # Step one, split out and merge customers and deliverables
    for event in events['value']:
        weekday = dateutil.parser.parse(event['start']['dateTime']).weekday()
        duration = dateutil.parser.parse(event['end']['dateTime']) - dateutil.parser.parse(event['start']['dateTime'])
        tempcust = []
        tempdeliverable = []
        for category in event['categories']:
            if category[0].isdigit():
                tempdeliverable.append(category)
            else:
                tempcust.append(category)
        if len(tempdeliverable) < 1:
            tempdeliverable.append("Others")
        if len(tempcust) < 1:
            tempcust.append("Others")

        duration = (duration + preparation_time)/len(tempdeliverable)
        for customer in tempcust:
            if not customer in timesheet:
                timesheet[customer] = {}
            for deliverable in tempdeliverable:
                if not deliverable in timesheet[customer]:
                    day = [timedelta(0)]*7
                    timesheet[customer][deliverable] = day
                timesheet[customer][deliverable][weekday] += duration

# Round all categories of all customers.
    for customer in timesheet:
        for deliverable in timesheet[customer]:
            for weekday in range(7):
                minutes = ceil(timesheet[customer][deliverable][weekday].seconds/(15*60))*15
                new_duration = timedelta(minutes=minutes)
                timesheet[customer][deliverable][weekday] = new_duration
                totaltime[weekday] += new_duration
                week_totaltime += new_duration

    totaltime[7] = week_totaltime


# Week Picker
    weekday = datetime.strptime( datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
    start_date = weekday - timedelta(days=weekday.weekday()+2) # Saturday before input_week
    end_date = start_date + timedelta(days=6)
    calendar = []
    selected_weekday=datetime.strptime(selected_date, "%Y-%m-%d")
    selected_start_date = selected_weekday - timedelta(days=selected_weekday.weekday()+2)
    if selected_weekday.weekday() >= 5:
      selected_start_date = selected_start_date + timedelta(days=7)

    for i in range(5):
        week = ["","",False] # 0 = weekstart, 1 = week text
        loop_start_date = start_date - timedelta(days=7*i) # Saturday before input_week
        loop_end_date = loop_start_date + timedelta(days=6)
        week[0] = loop_start_date.strftime("%Y-%m-%d")
        week[1] = loop_start_date.strftime("%Y-%m-%d") + " - " + loop_end_date.strftime("%Y-%m-%d")
        if loop_start_date == selected_start_date:
            week[2] = True
        calendar.append(week)


    context['calendar'] = calendar
    context['totaltime'] = totaltime
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
