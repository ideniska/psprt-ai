import face_recognition
from PIL import Image, ImageDraw

image = face_recognition.load_image_file(
    "/Users/denissakhno/Downloads/photo_test/IMG_nogb.jpg"
)
face_locations = face_recognition.face_locations(image)
print(face_locations)

pil_image = Image.fromarray(image)
draw = ImageDraw.Draw(pil_image)
draw.rectangle((face_locations[0]), outline=(0, 0, 255))
pil_image.show()
