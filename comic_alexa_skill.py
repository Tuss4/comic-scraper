from bs4 import BeautifulSoup
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor
)
from ask_sdk_core.utils import is_request_type, is_intent_name

from ask_sdk_model.ui import SimpleCard, StandardCard
from ask_sdk_model import Response

from dccomics import get_title_str as get_dc_title_str

import urllib.request
from datetime import timedelta, date
import logging


# Default intent globals
LAUNCH_MESSAGE = "So... you tryin ta hear what's new or naw?"
SKILL_NAME = "Latest Comics"
ASK_MESSAGE = "Which publisher?"
ASK_REPROMPT = "Marvel or DC?"
GET_COMICS_MESSAGE = "Here are the comics on sale this week, play-yah: "
# GET_COMICS_MESSAGE = "<audio src='https://s3-us-west-2.amazonaws.com/tuss4alexaskillaudioclips/new_comics.mp3' />"
HELP_MESSAGE = "You can say new comics, or, you can sayy exit... wassup?"
HELP_REPROMPT = "Sup fam?"
STOP_MESSAGE = "Stay fresh, cheese bags!"
FALLBACK_MESSAGE = "That is not how this works, homie."
FALLBACK_PROMPT = "Sup fam?"
EXCEPTION_MESSAGE = "<audio src='https://s3-us-west-2.amazonaws.com/tuss4alexaskillaudioclips/nah_bruh.mp3' />"

# Scraper globals
DATE_FMT = "%Y-%m-%d"
ADDR = "https://www.marvel.com/comics/calendar/week/{0}?byZone=marvel_site_zone&offset=0&tab=comic&formatType=issue&isDigital=0&byType=date&dateStart={1}&dateEnd={2}&orderBy=release_date+desc&limit=300&count=41"


# Scraper data retrieval functions
def get_sun_to_sat():
    today = date.today()
    dow_int = int(today.strftime('%w'))
    sunday = None
    if dow_int == 0:
        sunday = date.today()
    else:
        sunday = date.today() - timedelta(days=dow_int)
    saturday = sunday + timedelta(days=6)
    fmt_sun = sunday.strftime(DATE_FMT)
    fmt_sat =  saturday.strftime(DATE_FMT)
    return fmt_sun, fmt_sun, fmt_sat


def get_the_latest_titles():
    url = ADDR.format(*get_sun_to_sat())
    page = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(page, 'html.parser')
    titles = soup.findAll('h5')
    latest = [title.text.strip() for title in titles]
    # SSML does not support '&' sanitize accordingly
    clean = [l.replace('&', 'and') for l in latest]
    return clean


def get_latest_titles_str():
    return ", ".join(get_the_latest_titles())


# Skill classes and functions
# Adapted from https://github.com/alexa/skill-sample-python-fact/blob/master/lambda/py/lambda_function.py
sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WelcomeHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return(is_request_type("LaunchRequest")(handler_input))

    def handle(self, handler_input):
        logger.info("In WelcomeHandler")
        speech = "Welcome to {}!".format(SKILL_NAME)
        handler_input.response_builder.speak(speech).ask(ASK_REPROMPT).set_card(SimpleCard(SKILL_NAME, speech))

        return handler_input.response_builder.response


class LatestComicsHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("LatestComicsIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In LatestComicsHandler")

        slots = handler_input.request_envelope.request.intent.slots
        logger.info("GIVE ME SLOTS: ", slots)


        # data = get_latest_titles_str()
        speech = ASK_MESSAGE
        # speech = GET_COMICS_MESSAGE
        logger.info(speech)
        handler_input.response_builder.speak(speech).ask(ASK_REPROMPT).set_card(SimpleCard(SKILL_NAME, speech))

        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return(is_intent_name("AMAZON.CancelIntent")(handler_input) or
               is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(HELP_REPROMPT)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        # logger.info("Envelope: {}".format(handler_input.request_envelope.to_str()))
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.info("In CatchAllExceptionHandler")
        logger.info("Exception Envelope: {}".format(handler_input.request_envelope.to_str()))
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):

    def process(self, handler_input):
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
# sb.add_request_handler(WelcomeHandler())
sb.add_request_handler(WelcomeHandler())
sb.add_request_handler(LatestComicsHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
