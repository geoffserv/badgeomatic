"""badgeomatic_slackbot - the Slackbot portion of the badge robot

This module connects to slack, establishes a websocket, and then when we're
ready, sets off the event listener)

Take a look at readme_slack_app_setup.md for instructions on setting up
the slack-side bot & keys

Requirements
------------
slack-sdk : for slack things

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
import sys
import re
import requests
from urllib.parse import urlparse
import os


class Slackbot(object):
    def __init__(self):
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
        self.badgebot = badgeomatic_badgebot.Badgebot()

    def download_attachment(self, attachment_url):
        try:
            resp = requests.get(attachment_url,
                               headers={'Authorization':
                                        'Bearer %s' %
                                        badgeomatic_globals.config[
                                                'badgeomatic']['SlackTokenOA']})

            fname = os.path.basename(urlparse(attachment_url).path)
            badgeomatic_globals.debugger.message("INFO",
                                                 "fname: {}".format(
                                                     fname))
            assert not os.path.exists(fname), print(
                "File already exists. Please remove/rename and re-run")
            out_file = open(fname, mode="wb+")
            out_file.write(resp.content)
            out_file.close()
            return fname
        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)

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
            #     # client.web_client.reactions_add(
            #     #     name="eyes",
            #     #     channel=req.payload["event"]["channel"],
            #     #     timestamp=req.payload["event"]["ts"],
            #     # )

            # If it's a new message only with a file attachment,
            try:
                if req.payload["event"]["type"] == "message" \
                    and req.payload["event"].get("subtype") == "file_share":
                    badge_name = req.payload["event"]["text"]
                    file_url = req.payload["event"]["files"][0]["url_private"]
                    badgeomatic_globals.debugger.message("INFO",
                                                         "Badge Name: {}".format(
                                                             badge_name))
                    badgeomatic_globals.debugger.message("INFO",
                                                         "File URL: {}".format(
                                                             file_url))

                    if (len(badge_name) > 0) and \
                            (len(badge_name) < 30) and file_url:
                        badgeomatic_globals.debugger.message("INFO",
                                                             "Generating badge...")
                        photo_path = self.download_attachment(file_url)
                        self.badgebot.print_badge(badge_name, photo_path)
            except Exception as e:
                badgeomatic_globals.debugger.message("EXCP", e)

    def run(self):
        self.client.socket_mode_request_listeners.append(self.process)
        # Establish a WebSocket connection to the Socket Mode servers
        self.client.connect()
        # Just not to stop this process
        from threading import Event

        Event().wait()
