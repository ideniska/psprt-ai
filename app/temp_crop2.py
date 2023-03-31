import cv2
from rembg import remove
from PIL import Image


image = cv2.imread('/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/test_photo2.jpg')

# Detect face
face_cascade = cv2.CascadeClassifier(
    "/Users/denissakhno/Programming/Projects/psprt-ai/haarcascade_frontalface_default.xml.txt")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
(face_x, face_y, face_width, face_height) = faces[0]
total_height = image.shape[0]
total_width = image.shape[1]
center_h = total_height / 2
center_y = total_width / 2

# Calculate percentage of face height to image height
percentage = face_height / total_height
print(f"{face_height=}, {total_height=},{percentage=},{total_width=}")
print(f'{center_h=}, {center_y=}')


# Crop area above face and below face
cropped_image = image[0 + face_y - int(face_y*0.55):total_height-int(face_height*0.6), 0:total_width]  # Slicing to crop the image
cv2.imwrite('/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/test_crop4.jpg', cropped_image)

# Crop image for input size
cropped_image_height = cropped_image.shape[0]   # get image height (number of rows)
cropped_image_width = cropped_image.shape[1]    # get image width (number of columns)
aspect = cropped_image_width / cropped_image_height  # compute aspect ratio (width / height)
ideal_width = 590
ideal_height = 826
ideal_aspect = ideal_width / ideal_height   # set ideal aspect ratio

print(f'{aspect=:.2f}, {ideal_aspect=:.2f}')

if aspect > ideal_aspect:
    # Then crop the left and right edges:
    new_width = int(ideal_aspect * cropped_image_height)   # compute new width to keep ideal aspect ratio
    print(f'{new_width=}, {cropped_image_width=}')
    if 0 < new_width < cropped_image_width:   # check new width within image bounds
        offset = (cropped_image_width - new_width) / 2  # compute horizontal offset to center crop
        crop_params = [offset, 0, cropped_image_width - offset, cropped_image_height]   # set crop region
    else:
        crop_params = [0, 0, cropped_image_width, cropped_image_height]  # fall back to full image
else:
    # ... crop the top and bottom:
    new_height = int(cropped_image_width / ideal_aspect)   # compute new height to keep ideal aspect ratio
    print(f'{new_height=}, {cropped_image_height=}')
    if 0 < new_height < cropped_image_height:  # check new height within image bounds
        offset = (cropped_image_height - new_height) / 2  # compute vertical offset to center crop
        crop_params = [0, offset, cropped_image_width, cropped_image_height - offset]   # set crop region
    else:
        crop_params = [0, 0, cropped_image_width, cropped_image_height]  # fall back to full image

# Crop for document size
print(f'{crop_params=}')
if all(x >= 0 for x in crop_params) and crop_params[3] > crop_params[1] and crop_params[2] > crop_params[0]:
    # check crop region is valid (non-negative dimensions, positive width and height)
    cropped_image_after_size_crop = cropped_image[int(crop_params[1]):int(crop_params[3]), int(crop_params[0]):int(crop_params[2])]   # crop the image
    cv2.imwrite('/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/doc_size_cropped.jpg', cropped_image_after_size_crop)
else:
    print("Invalid crop dimensions:", crop_params)   # log error if crop failed

resized_image = cv2.resize(cropped_image_after_size_crop, (ideal_width, ideal_height), interpolation = cv2.INTER_AREA)
cv2.imwrite('/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/doc_size_cropped_resized2.jpg', resized_image)

# Remove bg and past it into new image with white bg
resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB) # convert color from opencv to pillow
pillow_image = Image.fromarray(resized_image)

output = remove(pillow_image, alpha_matting=False)
on_white_background = Image.new(
    "RGB", (ideal_width, ideal_height), (255, 255, 255)
)
on_white_background.paste(output, output)
on_white_background.save('/Users/denissakhno/Programming/Projects/psprt-ai/media/edited/final4.jpg')