# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
import plotly.graph_objects as go
import pandas as pd
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class ActionCovidInfo(Action):

    def name(self) -> Text:
        return "action_covid_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        message = '''
\nCOVID-19 is the disease caused by the new coronavirus that was first identified in December 2019.\n
COVID-19 symptoms include cough, fever or chills, shortness of breath or difficulty breathing, muscle or body aches, sore throat, new loss of taste or smell, diarrhea, headache, new fatigue, nausea or vomiting and congestion or runny nose. COVID-19 can be severe, and some cases have caused death.\n
The new coronavirus can be spread from person to person. It is diagnosed with a laboratory test.\n
There is no coronavirus vaccine yet. Prevention involves frequent hand-washing, coughing into the bend of your elbow, staying home when you are sick and wearing a cloth face covering if you can't practice physical distancing.\n
'''
        dispatcher.utter_message(text=message)

        return []

class ActionCovidSpread(Action):

    def name(self) -> Text:
        return "action_covid_spread"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        message = '''
\nThe virus is transmitted through direct contact with respiratory droplets of an infected person (generated through coughing and sneezing). Individuals can also be infected from and touching surfaces contaminated with the virus and touching their face (e.g., eyes, nose, mouth). The COVID-19 virus may survive on surfaces for several hours, but simple disinfectants can kill it.\n
'''
        dispatcher.utter_message(text=message)

        return []

class ActionCovidStateInfo(Action):

    def name(self) -> Text:
        return "action_covid_state_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']

        print(entities)
        state = "Not"
        for e in entities:
            if e['entity'] == 'state':
                state = e['value']
                break

        message = "No result for this state"
        if state != "Not":
            api_response = requests.get("https://api.covid19india.org/data.json").json()
            if state.title() == "India":
                res = api_response['statewise'][0]
                message = f"\n{state.title()} covid updates: \nActive cases = {res['active']}\nTotal Confirmed = {res['confirmed']}\nDeaths = {res['deaths']}\nLast updated Time = {res['lastupdatedtime']}\n"
            for res in api_response['statewise']:
                if res['state'] == state.title():
                    message = f"\n{state.title()} covid updates: \nActive cases = {res['active']}\nTotal Confirmed = {res['confirmed']}\nDeaths = {res['deaths']}\nLast updated Time = {res['lastupdatedtime']}\n"

        dispatcher.utter_message(text=f"{message}")

        return []

class ActionShowMap(Action):

    def name(self) -> Text:
        return "action_show_map"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        df = pd.read_csv("time_series_covid_19_confirmed.csv")
        df = df.rename(columns= {"Country/Region" : "Country", "Province/State": "Province"})

        total_list = df.groupby('Country')['2/27/21'].sum().tolist()

        country_list = df["Country"].tolist()
        country_set = set(country_list)
        country_list = list(country_set)
        country_list.sort()

        new_df = pd.DataFrame(list(zip(country_list, total_list)), 
                    columns =['Country', 'Total_Cases'])

        colors = ["#F9F9F5", "#FAFAE6", "#FCFCCB", "#FCFCAE",  "#FCF1AE", "#FCEA7D", "#FCD97D",
                "#FCCE7D", "#FCC07D", "#FEB562", "#F9A648",  "#F98E48", "#FD8739", "#FE7519",
                "#FE5E19", "#FA520A", "#FA2B0A", "#9B1803",  "#861604", "#651104", "#570303",]


        fig = go.Figure(data=go.Choropleth(
            locationmode = "country names",
            locations = new_df['Country'],
            z = new_df['Total_Cases'],
            text = new_df['Country'],
            colorscale = colors,
            autocolorscale=False,
            reversescale=False,
            colorbar_title = 'Reported Covid-19 Cases',
        ))

        fig.update_layout(
            title_text='Reported Covid-19 Cases',
            geo=dict(
                showcoastlines=True,
            ),
        )
        # fig.show()
        fig.write_html('first_figure.html')
        dispatcher.utter_message(text = "Map is displayed in the browser",attachment = fig.show())

        return []

class ActionCovidTips(Action):

    def name(self) -> Text:
        return "action_covid_tips"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        symp = "\n\nMost people who are infected with the SARS-CoV-2 virus have respiratory symptoms. They start to feel a little bit unwell, they will have a fever, they may have a cough or a sore throat or sneeze. In some individuals, they may have gastrointestinal symptoms. Others may lose the sense of smell or the sense of taste\n"
        prec = '''\n\nTo prevent the spread of COVID-19:\n\n
1. Clean your hands often. Use soap and water, or an alcohol-based hand rub.\n
2. Maintain a safe distance from anyone who is coughing or sneezing.\n
3. Wear a mask when physical distancing is not possible.\n
4. Don’t touch your eyes, nose or mouth.\n
5. Cover your nose and mouth with your bent elbow or a tissue when you cough or sneeze.\n
6. Stay home if you feel unwell.\n
7. If you have a fever, cough and difficulty breathing, seek medical attention.\n\n'''
        tips = f"Symptoms :{symp}\n\nPrecautions :{prec}"

        dispatcher.utter_message(text=f"{tips}")

        return []

class ActionSendMail(Action):

    def name(self) -> Text:
        return "action_send_mail"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        email = tracker.get_slot('emailid')
        print("email is ",email)
        print("Sending email.................")
        send_email(email)

        dispatcher.utter_message(text="Check Your Inbox.")

        return [SlotSet("emailid",None)]

class ActionCovidUpdates(Action):

    def name(self) -> Text:
        return "action_covid_updates"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = "No result."
        api_response = requests.get("https://api.covid19india.org/data.json").json()
        res = api_response['cases_time_series'][-1]
        message = f"\nCovid Updates: \nLast updated Time : {res['dateymd']}\nCases on {res['date']} : {res['dailyconfirmed']}\nTotal Deaths on {res['date']} : {res['dailydeceased']}\nDaily Recovered on {res['date']} : {res['dailyrecovered']}\nTotal Confirmed : {res['totalconfirmed']}\nDeaths : {res['totaldeceased']}\nTotal Recovered : {res['totalrecovered']}\n\n\tStay Safe!"
        
        dispatcher.utter_message(text=message)

        return []


def send_email(to_addr):
    from_addr = "testbot010400@gmail.com"
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address
    msg['From'] = from_addr
    # storing the receivers email address
    msg['To'] = to_addr
    # storing the subject

    msg['Subject'] = "COVID updates from chatbot"
    api_response = requests.get("https://api.covid19india.org/data.json").json()
    res = api_response['cases_time_series'][-1]
    message = f"\n\nCovid Updates: \n\nLast updated Time : {res['dateymd']}\nCases on {res['date']} : {res['dailyconfirmed']}\nTotal Deaths on {res['date']} : {res['dailydeceased']}\nDaily Recovered on {res['date']} : {res['dailyrecovered']}\nTotal Confirmed : {res['totalconfirmed']}\nDeaths : {res['totaldeceased']}\nTotal Recovered : {res['totalrecovered']}\n"
    d = "\nStay Safe!"
    symp = "\nMost people who are infected with the SARS-CoV-2 virus have respiratory symptoms. They start to feel a little bit unwell, they will have a fever, they may have a cough or a sore throat or sneeze. In some individuals, they may have gastrointestinal symptoms. Others may lose the sense of smell or the sense of taste\n"
    prec = '''\nTo prevent the spread of COVID-19:\n
1. Clean your hands often. Use soap and water, or an alcohol-based hand rub.\n
2. Maintain a safe distance from anyone who is coughing or sneezing.\n
3. Wear a mask when physical distancing is not possible.\n
4. Don’t touch your eyes, nose or mouth.\n
5. Cover your nose and mouth with your bent elbow or a tissue when you cough or sneeze.\n
6. Stay home if you feel unwell.\n
7. If you have a fever, cough and difficulty breathing, seek medical attention.\n\n'''
    tips = f"\nSymptoms :{symp}\n\nPrecautions :{prec}"
    final = message + tips + d
    body = final
    msg.attach(MIMEText(body, 'plain'))
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    # Authentication
    try:
        s.login(from_addr, "testingbot010400#")
        text = msg.as_string()
        s.sendmail(from_addr, to_addr, text)
    except:
        print("An Error occured while sending email.")
    finally:
        s.quit()