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

Functions
---------
tbd
"""

from PIL import Image, ImageFont, ImageDraw
from datetime import date

if __name__ == '__main__':
    badge_width = 639
    badge_height = 1014
    staff_photo_coords = (132, 137)
    staff_photo_width = 375

    text_name_coords_x = 320
    text_name_coords_y = 615

    text_date_coords_x = 320
    text_date_coords_y = 915

    # Fonts from
    badge_font = "fonts/Styrene/StyreneB-Medium.otf"

    badge_template = Image.open('images/boom-badges-standard-template-bkgnd-2022-05-13-02.png')
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
                               int((staff_photo_input_height / 2) - (staff_photo_input_width / 2)),
                               staff_photo_input_width,
                               int((staff_photo_input_height / 2) + (staff_photo_input_width / 2)))

    staff_photo = staff_photo.crop(staff_photo_crop_coords)

    staff_photo = staff_photo.resize((staff_photo_width, staff_photo_width))

    badge_composite = Image.new('RGB', (badge_width, badge_height), (0, 0, 0))

    badge_composite.paste(badge_template, (0, 0))
    badge_composite.paste(staff_photo, staff_photo_coords)

    text_name_width = badge_font_name.getlength(staff_name)
    text_date_width = badge_font_date.getlength(badge_date)

    badge_composite_draw = ImageDraw.Draw(badge_composite)
    badge_composite_draw.text((int(text_name_coords_x - (text_name_width / 2)),  # Center the name
                               text_name_coords_y),
                              staff_name,
                              (0, 0, 0),
                              font=badge_font_name)

    badge_composite_draw.text((int(text_date_coords_x - (text_date_width / 2)),  # Center the date
                               text_date_coords_y),
                              badge_date,
                              (0, 0, 0),
                              font=badge_font_date)

    badge_composite.show()
