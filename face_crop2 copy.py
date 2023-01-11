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

    top = y
    # Find the left and right most points of the head
    leftmost = x
    rightmost = x + width
    for i in range(y, y + height):
        for j in range(x, x + width):
            if not (image[i, j] == [255, 255, 255]).all():
                if j < leftmost:
                    leftmost = j
                if j > rightmost:
                    rightmost = j
                break
    rect_width = rightmost - leftmost + 5
    rect_height = height
    # Draw rectangle on the input image
    cv2.rectangle(
        image, (leftmost, top), (rightmost + 5, top + rect_height), (0, 0, 255), 2
    )

    # Get the path of the input image file
    dir_path = os.path.dirname(os.path.abspath(image_file))
    filename, file_extension = os.path.splitext(os.path.basename(image_file))

    # Construct the output image file path
    output_image_file = f"{dir_path}/{filename}_cropped{file_extension}"
    # Save the output image
    cv2.imwrite(output_image_file, image)
    return output_image_file


cropped_image_path = crop_head("/Users/denissakhno/Downloads/IMG_0510 (1).jpg")
