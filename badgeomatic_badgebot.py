"""badgeomatic_badgebot - the Badge generation portion of the badge robot

This module composites inputs from the slackbot and generates a badge

Requirements
------------
badgeomatic_globals : program-wide globals, debugger, etc
PIL : Pillow for graphic manipulation
datetime : dates.. and times
os : to handle local filesystem for downloads

Classes
-------
BadgeBot : generates badge layouts based on info from the slackbot
"""

import badgeomatic_globals
from PIL import Image, ImageFont, ImageDraw
from datetime import date
import os


class Badgebot(object):
    def __init__(self):
        self.badge_width = int(badgeomatic_globals.config['badgeomatic'][
            'BadgeWidth'])
        self.badge_height = int(badgeomatic_globals.config['badgeomatic'][
            'BadgeHeight'])
        self.staff_photo_coords = (
            int(badgeomatic_globals.config['badgeomatic'][
                    'StaffPhotoCoordsX']),
            int(badgeomatic_globals.config['badgeomatic'][
                    'StaffPhotoCoordsY']))
        self.staff_photo_width = int(badgeomatic_globals.config[
                                         'badgeomatic']['StaffPhotoWidth'])
        self.text_name_coords_x = int(badgeomatic_globals.config[
                                          'badgeomatic']['TextNameCoordsX'])
        self.text_name_coords_y = int(badgeomatic_globals.config[
                                          'badgeomatic']['TextNameCoordsY'])
        self.text_date_coords_x = int(badgeomatic_globals.config[
                                          'badgeomatic']['TextDateCoordsX'])
        self.text_date_coords_y = int(badgeomatic_globals.config[
                                          'badgeomatic']['TextDateCoordsY'])
        self.badge_font = badgeomatic_globals.config[
            'badgeomatic']['BadgeFont']
        self.badge_template = Image.open(badgeomatic_globals.config[
                                             'badgeomatic'][
                                             'BadgeTemplate'])
        # Here's where we'll store the badge images
        self.badge_image_path = badgeomatic_globals.config['badgeomatic'][
            'BadgeImageDir']

        # Create it if it doesn't exist
        try:
            if not os.path.exists(self.badge_image_path):
                os.makedirs(self.badge_image_path)
                badgeomatic_globals.\
                    debugger.message("INFO",
                                     "Created folder {}".format(
                                         self.badge_image_path))
        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)

    def print_badge(self, badge_name, photo_path):
        try:
            # Open the staff photo
            staff_photo = Image.open(photo_path)
            staff_name = badge_name

            # Date format for the printed date part of the badge
            badge_date = date.today().strftime("%b %d, %Y")

            # Some dumb name/font size scaling
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

            badge_font_name = ImageFont.truetype(self.badge_font,
                                                 staff_name_font_size)
            badge_font_date = ImageFont.truetype(self.badge_font, 50)

            staff_photo_input_width, staff_photo_input_height = staff_photo.\
                size

            # Assumes portrait photos, so width < height
            staff_photo_crop_coords = (0,
                                       int((staff_photo_input_height / 2) -
                                           (staff_photo_input_width / 2)),
                                       staff_photo_input_width,
                                       int((staff_photo_input_height / 2) +
                                           (staff_photo_input_width / 2)))

            # Graphic compositing block
            staff_photo = staff_photo.crop(staff_photo_crop_coords)

            staff_photo = staff_photo.resize((self.staff_photo_width,
                                              self.staff_photo_width))

            badge_composite = Image.new('RGB',
                                        (self.badge_width, self.badge_height),
                                        (0, 0, 0))

            badge_composite.paste(self.badge_template, (0, 0))
            badge_composite.paste(staff_photo, self.staff_photo_coords)

            text_name_width = badge_font_name.getlength(staff_name)
            text_date_width = badge_font_date.getlength(badge_date)

            badge_composite_draw = ImageDraw.Draw(badge_composite)
            badge_composite_draw.text((int(self.text_name_coords_x -
                                           (text_name_width / 2)),
                                       self.text_name_coords_y),
                                      staff_name,
                                      (0, 0, 0),
                                      font=badge_font_name)

            badge_composite_draw.text((int(self.text_date_coords_x -
                                           (text_date_width / 2)),
                                       self.text_date_coords_y),
                                      badge_date,
                                      (0, 0, 0),
                                      font=badge_font_date)
            badge_composite.show()

        except Exception as e:
            badgeomatic_globals.debugger.message("EXCP", e)
