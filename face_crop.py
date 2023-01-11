from PIL import Image

# Open the image
image = Image.open("/Users/denissakhno/Downloads/photo_test/IMG_0508_2.jpg")

# Get the width and height of the image
width, height = image.size

# Calculate the desired height of the head
desired_height = int(height * 0.5)  # 50% of the total height

# Select the face coordinates
face_coordinates = [(56, 44, 163, 151)]

# Crop the face from the image
face = image.crop(face_coordinates[0])

# Resize the face to the desired height
face = face.resize((int(face.width * (desired_height / face.height)), desired_height))

# Paste the resized face back onto the original image
image.paste(face, (face_coordinates[0][0], face_coordinates[0][1]))

# Save the edited image
image.save("/Users/denissakhno/Downloads/photo_test/IMG_0508_2_ed2.jpg")
