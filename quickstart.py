from __future__ import print_function

import datetime
import os.path
import math
import asyncio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

avail_hrs = 0
global start
start = datetime.datetime.utcnow()
rounded_min = int((math.ceil(start.minute/15)*15))
if(rounded_min > 45):  # Doesnt take into account overflow into the next day
    start = start.replace(hour=start.hour+1, minute=rounded_min%60, second=0, microsecond=0)
else:
    start = start.replace(minute=rounded_min, second=0, microsecond=0)
global end


async def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    workingHours()
    await createEvents()



async def createEvents():
    flag = True
    print("Enter Info When Prompted. Enter 'exit' As A Name To Exit.")
    tot_hrs = 0
    events = []
    while flag:
        clone = False
        name = str(input("Event Name: "))
        if(name.lower() == 'exit'):
            flag= False
            break
        length = int(input("How Long Do You Expect This Task To Complete (Minutes): "))
        if(length >= 90):
            length = length/2
            clone = True
        length = int(math.ceil(length/15) * 15)
        # if(tot_hrs + length >= avail_hrs):
        #     print("Not Enough Time In The Day!")
        #     break
        # tot_hrs += length
        difficulty = int(input("How Hard Is This Task (1-easy 2-medium 3-hard): "))
        if(clone == True):
            events.append(Event(name,length,difficulty))
        events.append(Event(name,length,difficulty))
    await eventQueue(events)
   #  await fillCal(events)

    
async def eventQueue(events):
    """Flips between hardest then easiest then second hardest, second easiest, etc.
    """
    new_order = []
    events.sort(key=lambda x: x.difficulty, reverse=True)

    s_break = Event("Break", 15, 0)
    m_break = Event("Break", 30, 0)

    while len(events) > 0:
        new_order.append(events[0])
        if(events[0].length >= 60):
            new_order.append(m_break)
        else:
            new_order.append(s_break)
        del events[0]
        if(len(events)>0):
            new_order.append(events[-1])
            if(events[-1].length >= 60):
                new_order.append(m_break)
            else:
                new_order.append(s_break)
            del events[-1]
    await fillCal(new_order)

def workingHours():
    flag = True
    while flag:
        print("Enter when you would like to call it a day?: ")
        end_hour = int(input("Hour (hh): "))
        end_min = int(input("Minute (mm): "))
        global end
        end = datetime.datetime.utcnow().replace(hour=end_hour, minute=end_min)
        end = myRound(end)
        if (end <= start):
            print("End of work day already passed. Enter valid end.")
        else:
            flag = False

    # THIS IS TO ENSURE THEY DONT GO OVERBOARD ON HOURS

    # new_date = datetime.datetime.now()
    # dif = (end.hour-start.hour)*60 + (end.min-start.min)
    # new_hours = dif % 60
    # new_min = dif-(new_hours * 60)
    # new_date = new_date.replace(hour=new_hours, minute=new_min)
    # print(new_date)
    # avail_hrs = (new_date.hour * 60) + (new_date.minute)

def myRound(x):
    rounded_min = int((math.ceil(x.minute/15)*15))
    if(rounded_min > 45):  # Doesnt take into account overflow into the next day
        x = x.replace(hour=x.hour+1, minute=rounded_min%60, second=0, microsecond=0)
    else:
        x = x.replace(minute=rounded_min, second=0, microsecond=0)
    return x


async def getPrevEvents():
    calendar = [False] * 96
    # global end
    # global start
    # creds = None
    # # The file token.json stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'credentials.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open('token.json', 'w') as token:
    #         token.write(creds.to_json())

    # try:
    #     service = build('calendar', 'v3', credentials=creds)     
    #     events_result = service.events().list(calendarId='primary', timeMax = end.isoformat()+"Z", timeMin=start.isoformat()+"Z",
    #                                           maxResults=10, singleEvents=True,
    #                                           orderBy='startTime').execute()
    #     events = events_result.get('items', [])  

     

    # except HttpError as error:
    #     print('An error occurred: %s' % error)

    # for event in events:
    #     start = event['start'].get('dateTime', event['start'].get('date'))
    #     end = event['end'].get('dateTime', event['end'].get('date'))
    #     print(start)
    #     print(end)
    global start
    global end
    start_in_min = ((start.hour * 60) + start.minute)/15
    print(start_in_min)
    end_in_min = ((end.hour * 60) + end.minute)/15
    print(end_in_min)


    i=0
    with open('./cal.txt','r') as file:
        lines = file.readlines()
    
    for line in lines:
        if(line != "True\n"):
            calendar[i] = False
        else:
            calendar[i] = True

        if(i <= start_in_min or i >= end_in_min):
            calendar[i] = True
        
        i+=1

    return calendar


async def fillCal(events):
    calendar = [False] * 96
    calendar = await getPrevEvents()
    # for event in events:
    #     start_index = event['start'].get('dateTime')
    #     start_index = datetime

    for event in events:
        required_slots = int(event.length / 15)
        for i in range(len(calendar)):
            if(calendar[i] is False and i+required_slots <= len(calendar)):
                fits = True
                         
                for j in range(i, i+required_slots):    
                    if calendar[j] == True:
                        fits = False
                        
                if fits:
                    for j in range(i, i+required_slots):
                        calendar[j] = True
                    event.start = datetime.datetime.utcnow()
                    start_hour = math.floor((i*15)/ 60)
                    start_min = (i*15) - start_hour*60    
                    event.start = event.start.replace(hour=start_hour, minute=start_min,second=0, microsecond=0)
                    event.end = datetime.datetime.utcnow()
                    end_hour = math.floor((i+required_slots) * 15 /60)
                    end_min = ((i+required_slots)*15) - end_hour*60
                    event.end = event.end.replace(hour=end_hour, minute=end_min, second=0,microsecond=0)
    
                    
                    await addEvent(event)
                    
                    break
    f = open("./cal.txt", "w")
    f.write('')
    f.close()
    for x in calendar:
        with open("./cal.txt", 'a') as cal:
            cal.write(str(x)+'\n')

    
async def addEvent(event):
    date = datetime.datetime.now()
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        new_event = {
            'summary': ""+str(event.name)+"",
            'description': 'A chance to hear more about Google\'s developer products.',
            'start': {
                'dateTime': ""+str(event.start.isoformat())+"",
                'timeZone': 'GMT-4:00',
            },
            'end': {
                'dateTime': ""+str(event.end.isoformat())+"",
                'timeZone': 'GMT-4:00',
            },   
            "reminders": {
                "useDefault": 'false',
                "overrides": [
                    {
                        "method":'popup',
                        "minutes": 1
                    }
                ]
            },                     
        }

        new_event = service.events().insert(calendarId='primary', body=new_event).execute()
        print ('Event created: %s' % (new_event.get('htmlLink')))
     

    except HttpError as error:
        print('An error occurred: %s' % error)
    
                    


    
    # Fill bool slots for already given things
    # Then parse thru, look for x consecutive, then x-1, etc.
    # If there is no space return an error, skip that task go to next one



class Event():

    def __init__(self, name, length, difficulty):
        self.name = name
        self.length = length
        self.start = datetime.datetime.utcnow()
        self.end = self.start
        self.difficulty = difficulty
        self.next = None
        # if(self.length > 90):
        #     new_length = round((self.length / 30)) * 15
        #     self.length = self.length - new_length
        #     self.next = Event(self.name, new_length, difficulty)    


if __name__ == '__main__':
    asyncio.run(main())