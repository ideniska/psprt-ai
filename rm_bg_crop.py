 face_cropped_input = Image.open(output_path)
        output = remove(face_cropped_input, alpha_matting=False)

        on_white_background = Image.new("RGB", output.size, (255, 255, 255))
        on_white_background.paste(output, output)
        # gray_image = on_white_background.convert("L")

        width, height = output.size

        # Initialize the crop coordinates to the full size of the image
        left = 0
        top = 0
        right = width
        bottom = height

        # # Find the leftmost and rightmost non-white pixels
        # for x in range(width):
        #     column = gray_image.crop((x, 0, x + 1, height))
        #     if column.getextrema() != (255, 255):
        #         left = x
        #         break

        # for x in range(width - 1, 0, -1):
        #     column = gray_image.crop((x, 0, x + 1, height))
        #     if column.getextrema() != (255, 255):
        #         right = x + 1
        #         break

        # # Find the topmost and bottommost non-white pixels
        # for y in range(height):
        #     row = gray_image.crop((0, y, width, y + 1))
        #     if row.getextrema() != (255, 255):
        #         top = y
        #         break

        # for y in range(height - 1, 0, -1):
        #     row = gray_image.crop((0, y, width, y + 1))
        #     if row.getextrema() != (255, 255):
        #         bottom = y + 1
        #         break

        # # Set the crop coordinates
        # crop_coords = (left, top, right, bottom)

        # # Crop the image
        # cropped_image = output.crop(crop_coords)

        original_width, original_height = output.size
        aspect_ratio = original_width / original_height

        desired_height = photo_size[1] - 1
        desired_width = int(desired_height / aspect_ratio)
        new_size = (desired_width, desired_height)
        resized = output.resize(new_size, resample=Image.Resampling.LANCZOS)

        white_background = Image.new("RGB", photo_size, (255, 255, 255))

        fg_width, fg_height = resized.size
        bg_width, bg_height = white_background.size

        # Calculate the coordinates of the top-left corner of the pasted image
        x = (bg_width - fg_width) // 2
        y = bg_height - fg_height

        white_background.paste(resized, (x, y), resized)
        white_background.save(output_path)



