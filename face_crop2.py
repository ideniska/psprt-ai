import os
import dlib
import cv2


def crop_head(image_file):
    # Load the image
    image = cv2.imread(image_file)

    # Create a HOG-based face detector
    face_detector = dlib.get_frontal_face_detector()

    # Detect faces in the image
    faces = face_detector(image, 1)

    # If no face found, return None
    if not faces:
        return None

    # Assume only one face in the image
    face = faces[0]

    # Get the location of the face
    x, y, width, height = face.left(), face.top(), face.width(), face.height()

    # Get the path of the input image file
    dir_path = os.path.dirname(os.path.abspath(image_file))
    filename, file_extension = os.path.splitext(os.path.basename(image_file))

    # Find the top non-white pixel of the input image
    for i in range(y):
        if not (image[i, x : x + width] == [255, 255, 255]).all():
            top = i
            break

    # Calculate the width of the rectangle
    rect_width = width + 10
    rect_height = y + height - top

    # Draw rectangle on the input image
    cv2.rectangle(image, (x, top), (x + rect_width, top + rect_height), (0, 0, 255), 2)

    # Construct the output image file path
    output_image_file = f"{dir_path}/{filename}_cropped{file_extension}"
    # Save the output image
    cv2.imwrite(output_image_file, image)
    return output_image_file


cropped_image_path = crop_head("/Users/denissakhno/Downloads/photo_example.png")
