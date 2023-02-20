from rembg import remove
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from .models import UserFile
from django.core.files import File
from django.core.files.storage import default_storage
import cv2
import os
from pathlib import Path
from django.conf import settings


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
        self.photo_size = self.sizes[photo_size]["size"]
        self.input_path = file_path
        self.file_id = file_id
        dir_path = os.path.dirname(os.path.abspath(self.input_path))
        self.filename, self.file_extension = os.path.splitext(
            os.path.basename(self.input_path)
        )
        self.clean_output_path = default_storage.path(
            "edited/{}_edited{}".format(self.filename, self.file_extension)
        )
        self.watermarked_output_path = default_storage.path(
            "watermarked/{}_watermarked{}".format(self.filename, self.file_extension)
        )

    def make(self):
        image = cv2.imread(self.input_path)

        # Detect face
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml.txt")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        (x, y, w, h) = faces[0]
        face_height = h
        total_height = image.shape[0]

        # Calculate percentage of face height to image height
        percentage = face_height / total_height

        # Get center coordinates and crop an image
        pillow_image = Image.open(self.input_path)
        x = pillow_image.size[0] / 2
        y = pillow_image.size[1] / 2
        w, h = pillow_image.size

        # Add zoom if face is too small
        if percentage < 0.6:
            zoom = 1 + 0.6 - percentage
            zoom = zoom * 2
        else:
            zoom = 1

        # Zoomed image
        pillow_image = pillow_image.crop(
            (x - w / zoom, y - h / zoom, x + w / zoom, y + h / zoom)
        )

        # Crop image for input size
        w, h = pillow_image.size
        aspect = w / float(h)
        ideal_width = self.photo_size[0]
        ideal_height = self.photo_size[1]
        ideal_aspect = ideal_width / float(self.photo_size[1])

        if aspect > ideal_aspect:
            # Then crop the left and right edges:
            new_width = int(ideal_aspect * h)
            offset = (w - new_width) / 2
            resize = (offset, 0, w - offset, h)
        else:
            # ... crop the top and bottom:
            new_height = int(w / ideal_aspect)
            offset = (h - new_height) / 2
            resize = (0, offset, w, h - offset)

        pillow_image = pillow_image.crop(resize).resize(
            (ideal_width, ideal_height), Image.LANCZOS
        )

        # Remove bg and past it into new image with white bg
        output = remove(pillow_image, alpha_matting=False)
        on_white_background = Image.new(
            "RGB", (ideal_width, ideal_height), (255, 255, 255)
        )
        on_white_background.paste(output, output)
        on_white_background.save(self.clean_output_path)

        ### Watermaked version ###
        watermark_image = on_white_background.copy()
        draw = ImageDraw.Draw(watermark_image)
        w, h = watermark_image.size
        x, y = int(w / 2), int(h / 2)
        if x > y:
            font_size = y
        elif y > x:
            font_size = x
        else:
            font_size = x

        font_path = os.path.join(
            settings.BASE_DIR, "app/static/fonts/Ubuntu-Medium.ttf"
        )
        font = ImageFont.truetype(font_path, int(font_size / 4))

        # add Watermark
        # (0,0,0)-black color text
        draw.text((x, y), "getvisa.photo", fill=(128, 128, 128), font=font, anchor="ms")
        draw.text(
            (x, y / 2), "getvisa.photo", fill=(128, 128, 128), font=font, anchor="ms"
        )
        draw.text(
            (x, y * 1.5), "getvisa.photo", fill=(128, 128, 128), font=font, anchor="ms"
        )
        watermark_image.save(self.watermarked_output_path)

        # Add watermarked image to UserFile model
        watermarked_file_name = os.path.basename(self.watermarked_output_path)
        watermarked_file_object = File(
            open(self.watermarked_output_path, "rb"), name=watermarked_file_name
        )

        new_watermarked_file_object = UserFile(
            file=watermarked_file_object,
            session=self.session_key,
            edited=True,
            prepared_for=self.prepared_for,
            watermarked=True,
        )
        new_watermarked_file_object.save()

        # Add clean (no watermark) image to UserFile model
        clean_file_name = os.path.basename(self.clean_output_path)
        clean_file_object = File(
            open(self.clean_output_path, "rb"), name=clean_file_name
        )

        new_clean_file_object = UserFile(
            file=clean_file_object,
            session=self.session_key,
            edited=True,
            prepared_for=self.prepared_for,
            watermarked=False,
        )
        new_clean_file_object.save()
