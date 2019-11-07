# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import datetime
import boto3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk.standard import StandardSkillBuilder

from ask_sdk_model import Response

from ask_sdk_s3.adapter import S3Adapter
from ask_sdk_core.skill_builder import CustomSkillBuilder

s3_client = boto3.client('s3')
s3_adapter = S3Adapter(bucket_name="amzn1-ask-skill-442eae5e-f577-buildsnapshotbucket-16fh383r9srj1", s3_client=s3_client)
sb = CustomSkillBuilder(persistence_adapter=s3_adapter)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to STUDY TIME. Let us study!"
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        persistence_attr['breaking'] = 'false'
        persistence_attr['studying'] = 'false'
        persistence_attr['breakhour'] = 0
        persistence_attr['breakminute'] = 0
        handler_input.attributes_manager.save_persistent_attributes()
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class StudyStartIntentHandler(AbstractRequestHandler):
    """Handler for Study Start Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StudyStartIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if not persistence_attr:
            persistence_attr['breaking'] = 'false'
            persistence_attr['studying'] = 'false'
            persistence_attr['breakhour'] = 0
            persistence_attr['breakminute'] = 0
            handler_input.attributes_manager.save_persistent_attributes()

        if persistence_attr['studying'] == 'false':
            DIFF_JST_FROM_UTC = 9
            current_time = datetime.datetime.now() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
            current_hour = current_time.hour
            current_minute = current_time.minute
            speak_output = "It is "+str(current_hour)+" "+str(current_minute)+". Do your best."
            persistence_attr['starthour'] = current_hour
            persistence_attr['startminute'] = current_minute
            persistence_attr['studying'] = 'true'
            persistence_attr['breakhour'] = 0
            persistence_attr['breakminute'] = 0
            handler_input.attributes_manager.save_persistent_attributes()
        else:
            speak_output = "Study time has already started. To finish the study time, please say Alexa, finish studying."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class BreakStartIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BreakStartIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if persistence_attr['breaking'] == 'false' and persistence_attr['studying'] == 'true':
            DIFF_JST_FROM_UTC = 9
            current_time = datetime.datetime.now() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
            current_hour = current_time.hour
            current_minute = current_time.minute
            speak_output = "You have got to be tired. It is "+str(current_hour)+" "+str(current_minute)+". To resume studying, please say Alexa, resume studying."
            persistence_attr['breakstarthour'] = current_hour
            persistence_attr['breakstartminute'] = current_minute
            persistence_attr['breaking'] = 'true'
            handler_input.attributes_manager.save_persistent_attributes()
        elif persistence_attr['studying'] == 'false':
            speak_output = "Study time has not started. To start study time, please say Alexa, start studying."
        else:
            speak_output = "Now you are on break. To resume studying, please say Alexa, resume studying."
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class BreakStopIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BreakStopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if persistence_attr['breaking'] == 'true':
            DIFF_JST_FROM_UTC = 9
            current_time = datetime.datetime.now() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
            current_hour = current_time.hour
            current_minute = current_time.minute
            break_start_hour = persistence_attr['breakstarthour']
            break_start_minute = persistence_attr['breakstartminute']
            break_time = current_time - datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day, hour=break_start_hour, minute=break_start_minute)
            def get_h_m(td):
                m, s = divmod(td.seconds, 60)
                h, m = divmod(m, 60)
                return h, m
            h, m = get_h_m(break_time)
            persistence_attr['breakhour'] += h
            persistence_attr['breakminute'] += m
            persistence_attr['breaking'] = 'false'
            handler_input.attributes_manager.save_persistent_attributes()
            speak_output = "It is "+str(current_hour)+" "+str(current_minute)+". Do your best."
        elif persistence_attr['studying'] == 'false':
            speak_output = "Study time has not started. To start study time, please say Alexa, start studying."
        else:
            speak_output = "You are not on break now. To have a break, please say Alexa, start a break."
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class StudyStopIntentHandler(AbstractRequestHandler):
    """Handler for Study Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StudyStopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistence_attr = handler_input.attributes_manager.persistent_attributes
        if persistence_attr['studying'] == 'false':
            speak_output = "Study time has not started. To start study time, please say Alexa, start studying."
        elif persistence_attr['studying'] == 'true' and persistence_attr['breaking'] == 'true':
            speak_output = "Now you are on break. To resume studying, please say Alexa, resume studying."
        else:
            DIFF_JST_FROM_UTC = 9
            current_time = datetime.datetime.now() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
            current_hour = current_time.hour
            current_minute = current_time.minute
            start_hour = persistence_attr['starthour']
            start_minute = persistence_attr['startminute']
            break_hour = persistence_attr['breakhour']
            break_minute = persistence_attr['breakminute']
            study_time = current_time - datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day, hour=start_hour, minute=start_minute) - datetime.timedelta(hours=break_hour, minutes=break_minute)
            def get_h_m(td):
                m, s = divmod(td.seconds, 60)
                h, m = divmod(m, 60)
                return h, m
            h, m = get_h_m(study_time)
            speak_output = "It is "+str(current_hour)+" "+str(current_minute)+". You have studied for "+str(h)+"hours and "+str(m)+"minutes. Thank you for using STUDY TIME."
            persistence_attr['breakhour'] = 0
            persistence_attr['breakminute'] = 0
            persistence_attr['breaking'] = 'false'
            persistence_attr['studying'] = 'false'
            handler_input.attributes_manager.save_persistent_attributes()
        

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "I calculate the time you are studying. Try to say, Alexa, start studying."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Thank you for using STUDY TIME"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speak_output = "I had a trouble doing what you asked. Please report the problem to the developer"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.




sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StudyStartIntentHandler())
sb.add_request_handler(StudyStopIntentHandler())
sb.add_request_handler(BreakStartIntentHandler())
sb.add_request_handler(BreakStopIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()