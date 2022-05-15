"""badgeomatic - Security badge photo compositor and printer thingie

I have this idea that we could take employee photos with a cell phone
Then send it to a slack channel from where-ever
My bot grabs the photo from the slack channel
Maybe does a little color balancing, cropping
Composites it with our badge template
Takes their name, the date, composites that
Remembers everything in a CSV for later import to the security system
And sends the print job to the HID Fargo printer

Requirements
------------
Pillow : Python graphic library
datetime : dates.. and times
atexit : trap exits
slack-sdk : for slack things

Functions
---------
tbd
"""
import os
import badgeomatic_globals
from PIL import Image, ImageFont, ImageDraw
from datetime import date
import atexit
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest


def badgeomatic_terminate():
    """Gracefully terminate the program.

    This should try to handle any final cleanup and close any open resources
    before exiting the program entirely
    """

    badgeomatic_globals.debugger.message("INFO",
                                         "Beginning program termination")

    # Show a debugger summary
    badgeomatic_globals.debugger.summary()

    badgeomatic_globals.debugger.exit("Completed program termination")


def badgeomatic_init():
    # Register the tto_terminate() function to run any time the program
    # terminates for any reason, using the atexit library.
    atexit.register(badgeomatic_terminate)


# Initialize SocketModeClient with an app-level token + WebClient
client = SocketModeClient(
    # This app-level token will be used only for establishing a connection
    # xapp-A111-222-xyz
    app_token=badgeomatic_globals.config['badgeomatic']['SlackTokenAL'],
    # You will be using this WebClient for performing
    # Web API calls in listeners
    # xoxb-111-222-xyz
    web_client=WebClient(
        token=badgeomatic_globals.config['badgeomatic']['SlackTokenOA'])
)


def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        # Acknowledge the request anyway
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        # Add a reaction to the message if it's a new message
        if req.payload["event"]["type"] == "message" \
            and req.payload["event"].get("subtype") is None:
            client.web_client.reactions_add(
                name="eyes",
                channel=req.payload["event"]["channel"],
                timestamp=req.payload["event"]["ts"],
            )
    if req.type == "interactive" \
        and req.payload.get("type") == "shortcut":
        if req.payload["callback_id"] == "hello-shortcut":
            # Acknowledge the request
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
            # Open a welcome modal
            client.web_client.views_open(
                trigger_id=req.payload["trigger_id"],
                view={
                    "type": "modal",
                    "callback_id": "hello-modal",
                    "title": {
                        "type": "plain_text",
                        "text": "Greetings!"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Good Bye"
                    },
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Hello!"
                            }
                        }
                    ]
                }
            )

    if req.type == "interactive" \
        and req.payload.get("type") == "view_submission":
        if req.payload["view"]["callback_id"] == "hello-modal":
            # Acknowledge the request and close the modal
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)


if __name__ == '__main__':
    """badgeomatic Main Function
    
    At this time, under development
    """

    badgeomatic_globals.debugger.message("INFO", "Beginning program execution")

    badgeomatic_init()

    client.socket_mode_request_listeners.append(process)
    # Establish a WebSocket connection to the Socket Mode servers
    client.connect()
    # Just not to stop this process
    from threading import Event

    Event().wait()

    """
    slack_token_al = badgeomatic_globals.config['badgeomatic']['SlackTokenAL']
    badgeomatic_globals.debugger.message("INFO", "slack_token_al: {}".format(
        slack_token_al))

    slack_token_oa = badgeomatic_globals.config['badgeomatic']['SlackTokenOA']
    badgeomatic_globals.debugger.message("INFO", "slack_token_oa: {}".format(
        slack_token_oa))

    badge_width = 639
    badge_height = 1014
    staff_photo_coords = (132, 137)
    staff_photo_width = 375

    text_name_coords_x = 320
    text_name_coords_y = 615

    text_date_coords_x = 320
    text_date_coords_y = 915

    # Fonts from
    badge_font = "fonts/StyreneB-Medium.otf"

    badge_template = Image.open(
        'images/boom-badges-standard-template-bkgnd-2022-05-13-02.png')
    staff_photo = Image.open('images/55E26909-7810-4423-9C75-F2DFA6BFEB5F.JPG')
    staff_name = "Tasmukanova"
    badge_date = date.today().strftime("%b %d, %Y")

    staff_name_len = len(staff_name)
    staff_name_font_size = 100  # Default
    if staff_name_len <= 3:
        staff_name_font_size = 150
    if (staff_name_len >= 7) and (staff_name_len <= 10):
        staff_name_font_size = 80
    if (staff_name_len >= 11) and (staff_name_len <= 16):
        staff_name_font_size = 70
    if staff_name_len >= 17:
        staff_name_font_size = 60

    badge_font_name = ImageFont.truetype(badge_font, staff_name_font_size)
    badge_font_date = ImageFont.truetype(badge_font, 50)

    staff_photo_input_width, staff_photo_input_height = staff_photo.size

    # Assumes portrait photos, so width < height
    staff_photo_crop_coords = (0,
                               int((staff_photo_input_height / 2) -
                                   (staff_photo_input_width / 2)),
                               staff_photo_input_width,
                               int((staff_photo_input_height / 2) +
                                   (staff_photo_input_width / 2)))

    staff_photo = staff_photo.crop(staff_photo_crop_coords)

    staff_photo = staff_photo.resize((staff_photo_width, staff_photo_width))

    badge_composite = Image.new('RGB', (badge_width, badge_height), (0, 0, 0))

    badge_composite.paste(badge_template, (0, 0))
    badge_composite.paste(staff_photo, staff_photo_coords)

    text_name_width = badge_font_name.getlength(staff_name)
    text_date_width = badge_font_date.getlength(badge_date)

    badge_composite_draw = ImageDraw.Draw(badge_composite)
    badge_composite_draw.text((int(text_name_coords_x - (text_name_width / 2)),
                               text_name_coords_y),
                              staff_name,
                              (0, 0, 0),
                              font=badge_font_name)

    badge_composite_draw.text((int(text_date_coords_x - (text_date_width / 2)),
                               text_date_coords_y),
                              badge_date,
                              (0, 0, 0),
                              font=badge_font_date)

    badge_composite.show()
    """
