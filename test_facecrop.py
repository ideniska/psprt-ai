import cv2
import numpy as np
import os

from PIL import Image


def adjust_image(image_path, output_size, face_area_percentage):
    dir_path = os.path.dirname(os.path.abspath(image_path))
    filename, file_extension = os.path.splitext(os.path.basename(image_path))
    output_path = f"{dir_path}/{filename}_cropped{file_extension}"
    # Open image using OpenCV
    image = cv2.imread(image_path)

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load face cascade
    face_cascade = cv2.CascadeClassifier(
        "/Users/denissakhno/Downloads/haarcascade_frontalface_default.xml.txt"
    )

    # Detect faces in image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Iterate through detected faces
    for (x, y, w, h) in faces:
        # Crop image to face area
        face_image = image[y : y + h, x : x + w]

    # Convert image to PIL Image
    face_image = Image.fromarray(face_image)

    # Resize image to desired output size
    face_image = face_image.resize((output_size[0], output_size[1]), Image.LANCZOS)

    # Calculate size of face area
    face_area_size = (output_size * face_area_percentage) / 100

    # Crop image again to desired face area size
    face_image = face_image.crop((0, 0, face_area_size, face_area_size))

    # Save final image to output path
    face_image.save(output_path)


adjust_image("/Users/denissakhno/Downloads/test_images/IMG_0514.jpg", (413, 531), 45)
