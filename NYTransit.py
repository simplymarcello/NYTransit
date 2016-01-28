"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from bs4 import BeautifulSoup
import requests

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[312071b7-232a-4ef5-a288-d9055940f049]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CheckTransit":
        return get_traffic_update(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome, to New York Transit. " \
                    "To request real time traffic data just say, Any delays on the 7 line? " \
                    "Or just say, 7 train."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "To request real time traffic updates just say, " \
                    "How's traffic for the R train? or," \
                    "Any delays on the 7 line? or,"\
                    "Traffic report, E train. or simply," \
                    "E Train."

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def pull_traffic_data(train):
    res = requests.get('http://assistive.usablenet.com/tt/www.mta.info/status/subway/{}'.format(train))
    soup = BeautifulSoup(res.content)
    div = soup.find("div", {"id" : "status_display"})
    result_string = ""
    for strings in div.stripped_strings:
        result_string += " " + strings
    if "The Service Status has changed." in result_string:
        result_string = "There are no updates for the {}".format(" , ".join(list(train)))
    return result_string

def get_traffic_update(intent, session):
    should_end_session = True
    if 'Train' in intent['slots']:
        if intent['slots']['Train']['value']:
            train = intent['slots']['Train']['value']
            if train in {'1','2','3'}:
                speech_output = pull_traffic_data('123')
            elif train in {'4','5','6'}:
                speech_output = pull_traffic_data('456')
            elif train in {'7'}:
                speech_output = pull_traffic_data('7')
            elif train in {'A','C','E','A.','C.','E.','a','c','e','a.','c.','e.'}:
                speech_output = pull_traffic_data('ACE')
            elif train in {'B','D','F','M','B.','D.','F.','M.','b','d','f','m','b.','d.','f.','m.'}:
                speech_output = pull_traffic_data('BDFM')
            elif train in {'G','G.','g','g.'}:
                speech_output = pull_traffic_data('G')
            elif train in {'J','Z','J.','Z.','j','z','j.','z.'}:
                speech_output = pull_traffic_data('JZ')
            elif train in {'L','L.','l','l.'}:
                speech_output = pull_traffic_data('L')
            elif train in {'N','Q','R','N.','Q.','R.','n','q','r','n.','q.','r.'}:
                speech_output = pull_traffic_data('NQR')
            elif train in {'S','S.','s','s.'}:
                speech_output = pull_traffic_data('S')
            else:
                speech_output = "I'm not sure which train your asking for. " \
                "Please try again."
                should_end_session = False
        else:
            speech_output = "I'm not sure which train your asking for. " \
                "Please try again."
            should_end_session = False
    else:
        speech_output = "I'm not sure which train your asking for. " \
                "Please try again."
        should_end_session = False

    reprompt_text = "To request real time traffic updates just say, " \
                    "How's traffic for the R train? or," \
                    "Any delays on the 7 line? or,"\
                    "Traffic report, E train. or simply," \
                    "E Train."


    card_title = intent['name']
    session_attributes = {}                  
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }