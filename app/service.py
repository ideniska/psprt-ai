from rembg import remove
from PIL import Image
from .models import UserFile
from django.core.files import File
from django.core.files.storage import default_storage

import os
from pathlib import Path


class PhotoPreparation:
    def __init__(self, photo_size, file_path, file_name, session_key, file_id):
        self.sizes = {
            "australia_passport": {
                "size": (413, 531),
                "head": 55,
            },
            "china_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "european_union_passport": {
                "size": (413, 531),
                "head": 55,
            },
            "schengen_visa": {
                "size": (413, 531),
                "head": 55,
            },
            "us_passport": {
                "size": (600, 600),
                "head": 55,
            },
            "india_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "japan_visa": {
                "size": (531, 531),
                "head": 55,
            },
            "us_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "canada_visa": {
                "size": (413, 531),
                "head": 55,
            },
            "canada_passport": {
                "size": (590, 826),
                "head": 55,
            },
        }
        self.session_key = session_key
        self.prepared_for = photo_size
        self.photo_size = self.sizes[photo_size]
        self.input_path = file_path
        self.file_id = file_id
        dir_path = os.path.dirname(os.path.abspath(self.input_path))
        self.filename, self.file_extension = os.path.splitext(
            os.path.basename(self.input_path)
        )
        # self.output_path = f"{dir_path}/{self.filename}_cropped{self.file_extension}"
        self.output_path = default_storage.path(
            "edited/{}_edited{}".format(self.filename, self.file_extension)
        )
        # self.output_path = f"/media/edited/{filename}{file_extension}"
        # self.output_path = file_path

    def make(self):
        input = Image.open(self.input_path)
        output = remove(input, alpha_matting=False)

        on_white_background = Image.new("RGB", output.size, (255, 255, 255))
        on_white_background.paste(output, output)
        gray_image = on_white_background.convert("L")

        width, height = output.size

        # Initialize the crop coordinates to the full size of the image
        left = 0
        top = 0
        right = width
        bottom = height

        # Find the leftmost and rightmost non-white pixels
        for x in range(width):
            column = gray_image.crop((x, 0, x + 1, height))
            if column.getextrema() != (255, 255):
                left = x
                break

        for x in range(width - 1, 0, -1):
            column = gray_image.crop((x, 0, x + 1, height))
            if column.getextrema() != (255, 255):
                right = x + 1
                break

        # Find the topmost and bottommost non-white pixels
        for y in range(height):
            row = gray_image.crop((0, y, width, y + 1))
            if row.getextrema() != (255, 255):
                top = y
                break

        for y in range(height - 1, 0, -1):
            row = gray_image.crop((0, y, width, y + 1))
            if row.getextrema() != (255, 255):
                bottom = y + 1
                break

        # Set the crop coordinates
        crop_coords = (left, top, right, bottom)

        # Crop the image
        cropped_image = output.crop(crop_coords)

        original_width, original_height = cropped_image.size
        aspect_ratio = original_width / original_height

        desired_height = self.photo_size["size"][1] - 1
        desired_width = int(desired_height / aspect_ratio)
        new_size = (desired_width, desired_height)
        resized = cropped_image.resize(new_size, resample=Image.LANCZOS)

        white_background = Image.new("RGB", self.photo_size["size"], (255, 255, 255))

        fg_width, fg_height = resized.size
        bg_width, bg_height = white_background.size

        # Calculate the coordinates of the top-left corner of the pasted image
        x = (bg_width - fg_width) // 2
        y = bg_height - fg_height

        white_background.paste(resized, (x, y), resized)
        white_background.save(self.output_path)

        # Add new edited image to UserFile model with the status EDITED
        edited_file_name = os.path.basename(self.output_path)
        edited_file_object = File(open(self.output_path, "rb"), name=edited_file_name)

        new_user_file_obj = UserFile(
            file=edited_file_object,
            session=self.session_key,
            edited=True,
            prepared_for=self.prepared_for,
        )
        new_user_file_obj.save()
