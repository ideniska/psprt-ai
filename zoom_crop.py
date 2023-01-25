from PIL import Image
import cv2
from rembg import remove


def make(input_path, ideal_width, ideal_height):
    # Load image
    image = cv2.imread(input_path)

    # Detect face
    face_cascade = cv2.CascadeClassifier(
        "/Users/denissakhno/Downloads/haarcascade_frontalface_default.xml.txt"
    )
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    (x, y, w, h) = faces[0]
    face_height = h
    total_height = image.shape[0]

    # Calculate percentage of face height to image height
    percentage = face_height / total_height

    # Get center coordinates and crop an image
    pillow_image = Image.open(input_path)
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
    ideal_aspect = ideal_width / float(ideal_height)

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
    on_white_background = Image.new("RGB", (ideal_width, ideal_height), (255, 255, 255))
    on_white_background.paste(output, output)
    return on_white_background


img = zoom_at("/Users/denissakhno/Downloads/test_images/IMG_0558.jpg", 600, 600)
img.save("/Users/denissakhno/Downloads/test_images/IMG_0558_zoomed.jpg")
