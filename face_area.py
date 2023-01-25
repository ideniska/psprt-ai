import cv2
import numpy as np
import os


def make(input_path, target_area):
    target_face_area_percentage = 60
    dir_path = os.path.dirname(os.path.abspath(input_path))
    filename, file_extension = os.path.splitext(os.path.basename(input_path))
    output_path = f"{dir_path}/{filename}_cropped{file_extension}"
    # Load the image
    img = cv2.imread(input_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use a pre-trained face detector to detect faces in the image
    face_cascade = cv2.CascadeClassifier(
        "/Users/denissakhno/Downloads/haarcascade_frontalface_default.xml.txt"
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Iterate through the detected faces
    for (x, y, w, h) in faces:
        # Draw a rectangle around the face
        # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Calculate the area of the bounding box around the face
        face_area = w * h
        print("Face area:", face_area)

        # Calculate the percentage of the image the face area takes up compared to the target area
        face_area_percentage = (face_area / (target_area[0] * target_area[1])) * 100
        print("Face area percentage: {:.2f}%".format(face_area_percentage))

        # Calculate the required width and height of the bounding box around the face
        target_face_area = (target_area[0] * target_area[1]) * (
            target_face_area_percentage / 100
        )
        print("target_face_area:", target_face_area)
        target_w = int(np.sqrt(target_face_area * w / h))
        target_h = int(np.sqrt(target_face_area * h / w))

        # Crop the image to the required size
        x_coordinate = x - (target_w - w) // 2
        y_coordinate = y - (target_h - h) // 2
        x_coordinate = max(x_coordinate, 0)
        y_coordinate = max(y_coordinate, 0)
        cropped_image = img[
            y_coordinate : y_coordinate + target_h,
            x_coordinate : x_coordinate + target_w,
        ]

        # Save the cropped image
        cv2.imwrite(output_path, cropped_image)


make("/Users/denissakhno/Downloads/test_images/IMG_0514.jpg", (413, 531))
