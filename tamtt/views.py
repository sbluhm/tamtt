from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tamtt.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, get_token
from tamtt.graph_helper import get_user, get_calendar_events, get_presence_events
import dateutil.parser
from datetime import datetime, timedelta
from math import ceil
import json
import os

def duration_decimal(td):
    total_seconds = int(td.total_seconds())
    hours = f'{total_seconds // 3600}'
    minutes = f'{(total_seconds % 3600) // 36:02d}'
    return '{}.{}'.format(hours, minutes)



# <HomeViewSnippet>
def home(request):
  context = initialize_context(request)

  return render(request, 'tamtt/home.html', context)
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
def calendar(request, textout = None):
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
  customer_totaltime = {}

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

        if not event['responseStatus']['response'] == "none":
            duration += preparation_time
        duration = duration/len(tempdeliverable)
        for customer in tempcust:
            if not customer in timesheet:
                timesheet[customer] = {}
                customer_totaltime[customer] = [timedelta(0)]*8
            for deliverable in tempdeliverable:
                if not deliverable in timesheet[customer]:
                    timesheet[customer][deliverable] = [timedelta(0)]*8
                timesheet[customer][deliverable][weekday] += duration

# Round all categories of all customers.
    for customer in timesheet:
        for deliverable in timesheet[customer]:
            for weekday in range(7):
                minutes = ceil(timesheet[customer][deliverable][weekday].seconds/(15*60))*15
                new_duration = timedelta(minutes=minutes)
                timesheet[customer][deliverable][weekday] = new_duration
                timesheet[customer][deliverable][7] += new_duration
                totaltime[weekday] += new_duration
                week_totaltime += new_duration
                customer_totaltime[customer][weekday] += new_duration
                customer_totaltime[customer][7] += new_duration 

    totaltime[7] = week_totaltime

# convert timedelta to decimal
    for customer in timesheet:
        for deliverable in timesheet[customer]:
            for weekday in range(8):
                timesheet[customer][deliverable][weekday] = duration_decimal(timesheet[customer][deliverable][weekday])
        for weekday in range(8):
            customer_totaltime[customer][weekday] = duration_decimal(customer_totaltime[customer][weekday])


# Week Picker
    weekday = datetime.strptime( datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
    if weekday.weekday() < 5:
        start_date = weekday - timedelta(days=weekday.weekday()+2) # Saturday before input_week
    else:
        start_date = weekday - timedelta(days=weekday.weekday()-5) # Saturday before input_week
    end_date = start_date + timedelta(days=6)
    calendar = []
    currentweek = []
    selected_weekday=datetime.strptime(selected_date, "%Y-%m-%d")
    selected_start_date = selected_weekday - timedelta(days=selected_weekday.weekday()+2)
    if selected_weekday.weekday() >= 5:
      selected_start_date = selected_start_date + timedelta(days=7)

    for i in range(5):
        week = ["","","","","","","","","",False] # 0-6 = date, 7 = start date text, 8  = week text, 9 = current week
        loop_start_date = start_date - timedelta(days=7*i) # Saturday before input_week
        loop_end_date = loop_start_date + timedelta(days=6)
        for j in range(7):
            week[j] = loop_start_date + timedelta(days=j)
        week[7] = week[0].strftime("%Y-%m-%d")
        week[8] = loop_start_date.strftime("%Y-%m-%d") + " - " + loop_end_date.strftime("%Y-%m-%d")
        if loop_start_date == selected_start_date:
            week[9] = True
            currentweek = week
        calendar.append(week)

# Sort data
    sorted_timesheet = {}
    for v in sorted(timesheet.keys()):
        sorted_timesheet[v] = {}
        for w in sorted(timesheet[v].keys()):
            sorted_timesheet[v][w] = timesheet[v][w]


# Pass data to template
    context['calendar'] = calendar                          # For week picker
    context['currentweek'] = currentweek
    context['totaltime'] = totaltime
    context['customer_totaltime'] = customer_totaltime 
    context['customer'] = sorted_timesheet
    fulldata = [currentweek[7], sorted_timesheet, currentweek[6].strftime("%Y-%m-%d"),currentweek[6].strftime("%m/%d/%Y"),currentweek[0].strftime("%a, %d %B %Y 00:00:00 GMT"), currentweek[6].strftime("%a, %d %B %Y 00:00:00 GMT"),customer_totaltime]
    if textout:
        print("Textout triggert")
        return json.dumps(fulldata)

  return render(request, 'tamtt/calendar.html', context)
# </CalendarViewSnippet>

# <CalenderViewDownload>
def calendar_download(request):
    json=calendar(request, True)
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define the full file path
    filepath = BASE_DIR + '/tamtt/salesforceimport.sh'
    # Open the file for reading content
    path = open(filepath, 'r')
    # Enrich script with timesheet JSON data
    shellscript = path.read().replace("TAMTT_VARIABLE_TIMESHEET_JSON", json)
    path.close()
    # Set the return value of the HttpResponse
    response = HttpResponse(shellscript, content_type='application/x-sh')
    # Set the HTTP header for sending to browser
    filename = json[2:12] + '.cmd'
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response
# </CalenderViewDownload>


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

  return render(request, 'tamtt/presence.html', context)
# </PresenceViewSnippet>
