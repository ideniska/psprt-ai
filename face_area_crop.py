import cv2
from rembg import remove
from PIL import Image
from PIL import ImageOps
import os


def visa_photo(input_image: str, input_size):
    sizes = {
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
    photo_size = sizes[input_size]["size"]
    dir_path = os.path.dirname(os.path.abspath(input_image))
    filename, file_extension = os.path.splitext(os.path.basename(input_image))
    output_path = f"{dir_path}/{filename}_pre{file_extension}"
    output_path_final = f"{dir_path}/{filename}_cropped{file_extension}"

    # Load image
    image = cv2.imread(input_image)

    # Detect face
    face_cascade = cv2.CascadeClassifier(
        "/Users/denissakhno/Downloads/haarcascade_frontalface_default.xml.txt"
    )
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Measure the height of the face and calculate the percentage of the total image height
    (x, y, w, h) = faces[0]
    print(x, y, w, h)
    face_height = h
    print("face_height", face_height)
    total_height = image.shape[0]
    print("total_height", total_height)
    percentage = (face_height / total_height) * 100
    print("initial percentage", percentage)

    # Crop the image if percentage is less than 50% or greater than 69%
    if percentage < 40:
        new_height = int(total_height * (1 - percentage / 100))
        print("new_height", new_height)
        y = y - (new_height - face_height) // 2
        print("New y", y)
        h = new_height

        cropped_image = image[y : y + h, 0 : image.shape[1]]
        # cropped_image = image[y : y + h, x : x + w]
        new_percentage = (face_height / new_height) * 100
        print("new percentage", new_percentage)
        # cv2.imwrite(output_path, cropped_image)
    else:
        cropped_image = image

    cv2.imwrite(output_path, cropped_image)

    #########################################
    input = Image.open(output_path)
    output = remove(input, alpha_matting=False)

    on_white_background = Image.new("RGB", input.size, (255, 255, 255))
    on_white_background.paste(output, output)
    # on_white_background.save(output_path_final)

    resized_on_whitebg = ImageOps.contain(on_white_background, photo_size)

    if resized_on_whitebg.height < photo_size[1]:
        new_image = Image.new(
            "RGB", (resized_on_whitebg.width, photo_size[1]), (255, 255, 255)
        )
        new_image.paste(
            resized_on_whitebg, (0, (photo_size[1] - resized_on_whitebg.height))
        )
        resized_on_whitebg = new_image

    resized_on_whitebg.save(output_path_final)


visa_photo(
    "/Users/denissakhno/Downloads/test_images/IMG_0558_crop_new.jpg",
    "australia_passport",
)
