from PIL import Image

image = Image.open("/Users/denissakhno/Downloads/test_images/IMG_0558.jpg")
width = image.size[0]
height = image.size[1]

aspect = width / float(height)

# ideal_width = 600
# ideal_height = 600
ideal_width = 413
ideal_height = 531

ideal_aspect = ideal_width / float(ideal_height)

if aspect > ideal_aspect:
    # Then crop the left and right edges:
    new_width = int(ideal_aspect * height)
    offset = (width - new_width) / 2
    resize = (offset, 0, width - offset, height)
else:
    # ... crop the top and bottom:
    new_height = int(width / ideal_aspect)
    offset = (height - new_height) / 2
    resize = (0, offset, width, height - offset)

thumb = image.crop(resize).resize((ideal_width, ideal_height), Image.ANTIALIAS)
thumb.save("/Users/denissakhno/Downloads/test_images/IMG_0558_crop_new.jpg")
