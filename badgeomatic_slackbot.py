"""badgeomatic_slackbot - the Slackbot portion of the badge robot

This module connects to slack, establishes a websocket, and then when we're
ready, sets off the event listener)

Take a look at readme_slack_app_setup.md for instructions on setting up
the slack-side bot & keys

Requirements
------------
badgeomatic_globals : program-wide globals, debugger, etc
badgeomatic_badgebot : receives photo & makes badge
slack-sdk : slack_sdk is for slack things
requests : for web requests, used to download the attachment
os : to handle local filesystem for downloads
datetime : dates.. and times

Classes
-------
SlackBot : Does the slack bot things
"""

import badgeomatic_globals
import badgeomatic_badgebot
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
import requests
import os
from datetime import date


class Slackbot(object):
    def __init__(self):
        # Set up a Socket Mode Client.  We'll receive updates from slack
        # via this socket.  It's an okay mechanism for very small scale use
        # of this bot
        self.client = SocketModeClient(
            # This app-level token is for establishing a connection
            # Looks like: xapp-A111-222-xyz
            app_token=badgeomatic_globals.config['badgeomatic']
            ['SlackTokenAL'],
            # This WebClient performs Web API calls in listeners
            # Looks like: xoxb-111-222-xyz
            web_client=WebClient(
                token=badgeomatic_globals.config['badgeomatic']
                ['SlackTokenOA'])
        )

        # Here's where we'll store the portrait images
        self.portrait_image_path = badgeomatic_globals.config['badgeomatic'][
            'PortraitImageDir']

        # Create it if it doesn't exist
        try:
            if not os.path.exists(self.portrait_image_path):
                os.makedirs(self.portrait_image_path)
                badgeomatic_globals.debugger.\
                    message("INFO", "Created folder {}".
                            format(self.portrait_image_path))

        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)

        # Lets make sure it exists
        assert os.path.exists(self.portrait_image_path), \
            badgeomatic_globals.debugger.message("ASRT",
                                                 "Can't find badge folder {}".
                                                 format(self.
                                                        portrait_image_path))

        # Set ourself up a badgebot
        try:
            self.badgebot = badgeomatic_badgebot.Badgebot()
        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)

    def download_attachment(self, badge_name, attachment_url):
        try:
            request_headers = {'Authorization': 'Bearer %s' %
                                                badgeomatic_globals.config[
                                                 'badgeomatic'][
                                                 'SlackTokenOA']}

            request = requests.get(attachment_url, headers=request_headers)

            filename_datestamp = date.today().strftime("%Y-%m-%d-%H-%M-%S")
            filename = "{}{}-{}.jpg".format(self.portrait_image_path,
                                            badge_name,
                                            filename_datestamp)
            badgeomatic_globals.debugger.message("INFO",
                                                 "filename: {}".format(
                                                     filename))

            assert not os.path.exists(filename), badgeomatic_globals.debugger.\
                message("ASRT", "Badge already exists %s".format(filename))

            out_file = open(filename, mode="wb+")
            out_file.write(request.content)
            out_file.close()

            return filename

        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)

        return False

    def process(self, client: SocketModeClient, req: SocketModeRequest):
        if req.type == "events_api":
            # Acknowledge the request anyway
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)

            badgeomatic_globals.debugger.message("INFO",
                                                 "Slack event: {}".format(
                                                     req.payload))

            # If it's a new message only without a file,
            # if req.payload["event"]["type"] == "message" \
            #     and req.payload["event"].get("subtype") is None:
            #    Pass

            # If it's a new message only with a file attachment,
            try:
                if req.payload["event"]["type"] == "message" \
                        and req.payload["event"].get("subtype") == \
                        "file_share":

                    # Badge name will be whatever text is with the image
                    badge_name = req.payload["event"]["text"]

                    # The attachment URL, must be downloaded separately
                    file_url = req.payload["event"]["files"][0]["url_private"]

                    badgeomatic_globals.debugger.message("INFO",
                                                         "Badge Name: {}".
                                                         format(badge_name))
                    badgeomatic_globals.debugger.message("INFO",
                                                         "File URL: {}".format(
                                                             file_url))

                    # Only consider names between 1 and 29 chars
                    if (len(badge_name) > 0) and \
                            (len(badge_name) < 30) and file_url:
                        badgeomatic_globals.debugger.message("INFO",
                                                             "Generating "
                                                             "badge...")
                        photo_path = self.download_attachment(badge_name,
                                                              file_url)
                        self.badgebot.print_badge(badge_name, photo_path)
                    else:
                        badgeomatic_globals.debugger.message("INFO",
                                                             "Name too short "
                                                             "or too long to "
                                                             "generate")
            except Exception as e:
                badgeomatic_globals.debugger.message("EXCP", e)

    def run(self):
        # noinspection PyTypeChecker
        self.client.socket_mode_request_listeners.append(self.process)
        # Establish a WebSocket connection to the Socket Mode servers
        self.client.connect()
        # Just not to stop this process
        from threading import Event

        Event().wait()
