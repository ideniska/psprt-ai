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
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class PhotoPreparation:
    def __init__(self, photo_size, file_path, session_key, file_id):
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
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     self.session_key,
        #     {
        #         "type": "celery_task_update",
        #         "data": {
        #             "progress": 0.2,
        #             "event": "make_started",
        #         },
        #     },
        # )
        image = cv2.imread(self.input_path)

        # Detect face
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml.txt")

        # async_to_sync(channel_layer.group_send)(
        #     self.session_key,
        #     {
        #         "type": "celery_task_update",
        #         "data": {
        #             "progress": 0.3,
        #             "event": "face_detected",
        #         },
        #     },
        # )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        (face_x, face_y, face_width, face_height) = faces[0]
        total_height = image.shape[0]
        total_width = image.shape[1]
        center_h = total_height / 2
        center_y = total_width / 2

        # Calculate percentage of face height to image height
        percentage = face_height / total_height

        # Crop area above face and below face
        cropped_image = image[
            0 + face_y - int(face_y * 0.55) : total_height - int(face_height * 0.6),
            0:total_width,
        ]  # Slicing to crop the image

        # Crop image for input size
        cropped_image_height = cropped_image.shape[
            0
        ]  # get image height (number of rows)
        cropped_image_width = cropped_image.shape[
            1
        ]  # get image width (number of columns)
        aspect = (
            cropped_image_width / cropped_image_height
        )  # compute aspect ratio (width / height)
        ideal_width = self.photo_size[0]
        ideal_height = self.photo_size[1]
        ideal_aspect = ideal_width / ideal_height  # set ideal aspect ratio

        if aspect > ideal_aspect:
            # Then crop the left and right edges:
            new_width = int(
                ideal_aspect * cropped_image_height
            )  # compute new width to keep ideal aspect ratio
            print(f"{new_width=}, {cropped_image_width=}")
            if (
                0 < new_width < cropped_image_width
            ):  # check new width within image bounds
                offset = (
                    cropped_image_width - new_width
                ) / 2  # compute horizontal offset to center crop
                crop_params = [
                    offset,
                    0,
                    cropped_image_width - offset,
                    cropped_image_height,
                ]  # set crop region
            else:
                crop_params = [
                    0,
                    0,
                    cropped_image_width,
                    cropped_image_height,
                ]  # fall back to full image
        else:
            # ... crop the top and bottom:
            new_height = int(
                cropped_image_width / ideal_aspect
            )  # compute new height to keep ideal aspect ratio
            print(f"{new_height=}, {cropped_image_height=}")
            if (
                0 < new_height < cropped_image_height
            ):  # check new height within image bounds
                offset = (
                    cropped_image_height - new_height
                ) / 2  # compute vertical offset to center crop
                crop_params = [
                    0,
                    offset,
                    cropped_image_width,
                    cropped_image_height - offset,
                ]  # set crop region
            else:
                crop_params = [
                    0,
                    0,
                    cropped_image_width,
                    cropped_image_height,
                ]  # fall back to full image

        # Crop for document size
        if (
            all(x >= 0 for x in crop_params)
            and crop_params[3] > crop_params[1]
            and crop_params[2] > crop_params[0]
        ):
            # check crop region is valid (non-negative dimensions, positive width and height)
            cropped_image_after_size_crop = cropped_image[
                int(crop_params[1]) : int(crop_params[3]),
                int(crop_params[0]) : int(crop_params[2]),
            ]  # crop the image
            cv2.imwrite(
                "/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/doc_size_cropped.jpg",
                cropped_image_after_size_crop,
            )
        else:
            print("Invalid crop dimensions:", crop_params)  # log error if crop failed

        # async_to_sync(channel_layer.group_send)(
        #     self.session_key,
        #     {
        #         "type": "celery_task_update",
        #         "data": {
        #             "progress": 0.4,
        #             "event": "cropped_image_after_size_crop",
        #         },
        #     },
        # )

        resized_image = cv2.resize(
            cropped_image_after_size_crop,
            (ideal_width, ideal_height),
            interpolation=cv2.INTER_AREA,
        )

        # Remove bg and past it into new image with white bg
        resized_image = cv2.cvtColor(
            resized_image, cv2.COLOR_BGR2RGB
        )  # convert color from opencv to pillow
        pillow_image = Image.fromarray(resized_image)

        output = remove(pillow_image, alpha_matting=False)
        on_white_background = Image.new(
            "RGB", (ideal_width, ideal_height), (255, 255, 255)
        )
        on_white_background.paste(output, output)
        on_white_background.save(self.clean_output_path)

        # async_to_sync(channel_layer.group_send)(
        #     self.session_key,
        #     {
        #         "type": "celery_task_update",
        #         "data": {
        #             "progress": 0.5,
        #             "event": "before watermarks image saved",
        #         },
        #     },
        # )

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

        # async_to_sync(channel_layer.group_send)(
        #     self.session_key,
        #     {
        #         "type": "celery_task_update",
        #         "data": {
        #             "progress": 0.6,
        #             "event": "watermarked image saved",
        #         },
        #     },
        # )

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
