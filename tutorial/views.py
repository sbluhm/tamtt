#TODO: Sort categories alphabetically.
#TODO: Handle parallel meetings sensibly.


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
  if request.GET.get('week'):
    events = get_calendar_events(token, request.GET['week'])
  else:
    events = get_calendar_events(token)

  timesheet = {}
  totaltime = [datetime.timedelta(0)]*8 # 8 will be the week total
  week_totaltime = datetime.timedelta(0)

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

                if not customer in timesheet:
                    timesheet[customer] = {}

                # add to existing deliverables here
                if not temp_deliverable['category'] in timesheet[customer]:
                    day = [datetime.timedelta(0)]*7
                    timesheet[customer][temp_deliverable['category']] = day
                duration = dateutil.parser.parse(event['end']['dateTime']) - dateutil.parser.parse(event['start']['dateTime'] )
                weekday = dateutil.parser.parse(event['start']['dateTime']).weekday()
                timesheet[customer][temp_deliverable['category']][weekday] += duration
                totaltime[weekday] += duration
                week_totaltime += duration

        else:
            temp_deliverable['category'] = "Others"

#            newtimesheet["Others"].append(deliverables)

    totaltime[7] = week_totaltime

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
