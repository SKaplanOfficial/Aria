import re
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw

from ariautils import command_utils, io_utils
from ariautils.misc_utils import any_in_str

class ImgCmd(command_utils.Command):
    info = {
        "title": "Image Management for Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras/",
        'id': "aria_extra_img",
        "version": "1.0.0",
        "description": """
            This command offers various images management and manipulation functionalities supported by Aria's contextual awareness.
        """,
        "requirements": {},
        "extensions": {},
        "purposes": [
            "flip ./img.png horizontally", "rotate these images 90 deg clockwise", "resize this to 300x300", "make all of these grayscale"
        ],
        "targets": [
            "./img.png", "./folder_of_images", "these images", "this image", "this", "these"
        ],
        "keywords": [
            "aria", "command", "extra", "image", "contextual", "utility"
        ],
        "example_usage": [
            ("increase the contrast of this", "Increase the contrast of the selected image by a factor of 2."),
            ("increase the contrast of these by a factor of 1.2", "Increase the contrast of the selected images by a factor of 1.2."),
            ("find the edges in this", "Run edge detection on the selected image."),
            ("add a circle mask to these", "Add a circular mask over the selected images, positioned at the center of each image."),
            ("brighten this", "Brighten the selected image by a factor of 2."),
            ("rotate this 90 degrees right", "Rotate the selected image 90 degrees clockwise."),
            ("flip this horizontally", "Flip the selected image across the y axis (from left to right)."),
            ("add a 30 pixel border to each of these", "Add a 30 pixel white border to each of the selected images."),
        ],
        "help": [
            "As of now, you must select items in Finder for any of the functions to work.",
        ],
        "contact_details": {
            "author": "Stephen Kaplan",
            "email": "stephen.kaplan@maine.edu",
            "website": "http://skaplan.io",
        },
        "info_version": "0.9.0",
    }

    def execute(self, query, origin):
        parts = query.split()
        query_type = self.get_query_type(query, get_tuple = True)

        if query_type[0] >= 5000:
            # Operate on selected files in Finder
            selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
            if selected_items != None:
                for item in selected_items:
                    self.__operate_in_place(item, query_type[1]["func"], query_type[1]["args"])

    # I/O
    def __operate_in_place(self, path, operation, args):
        img = Image.open(path)
        img = operation(img, *args)

        if img.mode == "RGBA" and (path.lower().endswith(".jpg") or path.lower().endswith(".jpeg")):
            path = path.replace(".JPEG", ".png").replace(".JPG", ".png").replace(".jpeg", ".png").replace(".jpg", ".png")

        img.save(path)
        io_utils.sprint("Operation complete.")

    # Flipping
    def __flip_h(self, image, _args = []):
        io_utils.sprint("Flipping horizontally...")
        return image.transpose(Image.FLIP_LEFT_RIGHT)

    def __flip_v(self, image, _args = []):
        io_utils.sprint("Flipping vertically...")
        return image.transpose(Image.FLIP_TOP_BOTTOM)

    def __mirror(self, image, _args = []):
        io_utils.sprint("Mirroring...")
        return ImageOps.mirror(image)

    # Rotation
    def __rotate_clockwise(self, image, angle, _args = []):
        io_utils.sprint("Rotating clockswise...")
        return image.rotate(angle = -angle)

    def __rotate_counterclockwise(self, image, counterclock_angle, _args = []):
        io_utils.sprint("Rotating counterclockwise...")
        return image.rotate(angle = counterclock_angle)


    # Resizing
    def __resize(self, image, new_width, new_height, _args = []):
        io_utils.sprint("Resizing...")
        return image.resize((new_width, new_height), Image.ANTIALIAS)

    def __scale(self, image, scale_factor = 2, _args = []):
        io_utils.sprint("Rescaling...")
        return ImageOps.scale(image, scale_factor)

    def __add_border(self, image, border_width, border_color = 255):
        io_utils.sprint("Adding border...")
        return ImageOps.expand(image, int(border_width), border_color)

    # Enhancements
    def __enhance_color(self, image, enhance_factor = 2, _args = []):
        io_utils.sprint("Enhancing color...")
        return ImageEnhance.Brightness(image).enhance(enhance_factor)

    def __enhance_contrast(self, image, enhance_factor = 2, _args = []):
        io_utils.sprint("Enhancing contrast...")
        return ImageEnhance.Contrast(image).enhance(enhance_factor)

    def __enhance_brightness(self, image, enhance_factor = 2, _args = []):
        io_utils.sprint("Enhancing brightness...")
        return ImageEnhance.Brightness(image).enhance(enhance_factor)

    def __enhance_sharpness(self, image, enhance_factor = 2, _args = []):
        io_utils.sprint("Enhancing sharpness...")
        return ImageEnhance.Sharpness(image).enhance(enhance_factor)


    # Filters
    def __basic_filter(self, image, filter):
        pass

    def __blur(self, image, _args = []):
        io_utils.sprint("Blurring...")
        return image.filter(filter = ImageFilter.BLUR)

    def __contour(self, image, _args = []):
        io_utils.sprint("Contouring...")
        return image.filter(filter = ImageFilter.CONTOUR)

    def __detail(self, image, _args = []):
        io_utils.sprint("Detailing...")
        return image.filter(filter = ImageFilter.DETAIL)

    def __enhance_edges(self, image, _args = []):
        io_utils.sprint("Enhancing edges...")
        return image.filter(filter = ImageFilter.EDGE_ENHANCE)

    def __enhance_edges_more(self, image, _args = []):
        io_utils.sprint("Enhancing edges...")
        return image.filter(filter = ImageFilter.EDGE_ENHANCE_MORE)

    def __find_edges(self, image, _args = []):
        io_utils.sprint("Finding edges...")
        return image.filter(filter = ImageFilter.FIND_EDGES)

    def __emboss(self, image, _args = []):
        io_utils.sprint("Embossing...")
        return image.filter(filter = ImageFilter.EMBOSS)

    def __sharpen(self, image, _args = []):
        io_utils.sprint("Sharpening...")
        return image.filter(filter = ImageFilter.SHARPEN)

    def __smooth(self, image, _args = []):
        io_utils.sprint("Smoothing...")
        return image.filter(filter = ImageFilter.SMOOTH)

    def __smooth_more(self, image, _args = []):
        io_utils.sprint("Smoothing...")
        return image.filter(filter = ImageFilter.SMOOTH_MORE)

    def __grayscale(self, image, _args = []):
        io_utils.sprint("Removing color...")
        return ImageOps.grayscale(image)
    
    def __invert(self, image, _args = []):
        io_utils.sprint("Inverting...")
        return ImageOps.invert(image)

    def __posterize(self, image, num_bits = 4, _args = []):
        io_utils.sprint("Posterizing...")
        return ImageOps.posterize(image, num_bits)

    def __solarize(self, image, greyscale_threshold = 128, _args = []):
        io_utils.sprint("Solarizing...")
        return ImageOps.solarize(image, greyscale_threshold)


    # Masks
    def __circle_mask(self, image, scale, _args = []):
        large_dim = (image.size[0] * 3, image.size[1] * 3)
        mask = Image.new('L', large_dim, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + large_dim, fill = 255)
        mask = mask.resize(image.size, Image.ANTIALIAS)
        image.putalpha(mask)
        return image

    def check_for_img_target(self, string):
        return any_in_str([".png", ".jpg", ".jpeg", ".tiff", ".webp", ".raw", ".pdf", ".svg", ".heif"], string.lower())

    def get_query_type(self, query, get_tuple = False):
        parts = query.split()

        selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
        has_image_target = self.check_for_img_target(query)

        if len(selected_items) > 0:
            if not has_image_target:
                for item in selected_items:
                    if self.check_for_img_target(item):
                        has_image_target = True
                        break


        __query_type_map = {
            # Scale
            300: {
                "conditions": [has_image_target, any_in_str(["scale", "enlargen", "embiggen", "larger"], query) or ("size" in query and "up" in query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__scale,
                "args": [1 + float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            301: {
                "conditions": [has_image_target, any_in_str(["scale", "enlargen", "embiggen", "larger"], query) or ("size" in query and "up" in query), any_in_str(["factor", "times", "points"], query)],
                "func": self.__scale,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            302: {
                "conditions": [has_image_target, any_in_str(["scale", "shrink", "decrease", "smaller"], query) or ("size" in query and "down" in query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__scale,
                "args": [float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            303: {
                "conditions": [has_image_target, any_in_str(["scale", "shrink", "decrease", "smaller"], query) or ("size" in query and "down" in query), any_in_str(["factor", "divided"], query)],
                "func": self.__scale,
                "args": [1/float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            304: {
                "conditions": [has_image_target, any_in_str(["scale", "enlargen", "embiggen", "larger"], query) or ("size" in query and "up" in query)],
                "func": self.__scale,
                "args": [2],
            },
            305: {
                "conditions": [has_image_target, any_in_str(["scale", "shrink", "decrease", "smaller"], query) or ("size" in query and "down" in query)],
                "func": self.__scale,
                "args": [1/2],
            },

            # Border
            306: { # Border with color
                "conditions": [has_image_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge"], query) or ("spacing" in query and "around" in query), any_in_str(["of", "with", "px", "pixel", "spacing"], query), "color" in query],
                "func": self.__add_border,
                "args": re.compile(r'(?:color of |add a )([0-9]+|.*)').findall(query),
            },
            307: { # Border with width
                "conditions": [has_image_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge"], query) or ("spacing" in query and "around" in query), any_in_str(["of", "with", "px", "pixel", "spacing"], query)],
                "func": self.__add_border,
                "args": re.compile(r'([0-9]+)').findall(query),
            },
            308: { # Default border - 10 pixels
                "conditions": [has_image_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge"], query) or ("spacing" in query and "around" in query)],
                "func": self.__add_border,
                "args": [10],
            },

            # Enhancements
            309: { # COLOR Enhance with factor
                "conditions": [has_image_target, any_in_str(["enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "color" in query, any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_color,
                "args": [1 + float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            310: {
                "conditions": [has_image_target, any_in_str(["enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "color" in query, any_in_str(["factor", "times", "points"], query)],
                "func": self.__enhance_color,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            311: {
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "color" in query, any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_color,
                "args": [float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            312: {
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "color" in query, any_in_str(["factor", "divided"], query)],
                "func": self.__enhance_color,
                "args": [1/float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            313: { # Default increase color - 2x
                "conditions": [has_image_target, any_in_str(["enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "color" in query],
                "func": self.__enhance_color,
                "args": [2],
            },
            314: { # Default decrease color - 1/2x
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "color" in query],
                "func": self.__enhance_color,
                "args": [1/2],
            },
            315: { # CONTRAST enhance with factor
                "conditions": [has_image_target, any_in_str(["enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "contrast" in query, any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_contrast,
                "args": [1 + float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            316: {
                "conditions": [has_image_target, any_in_str(["enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "contrast" in query, any_in_str(["factor", "times", "points"], query)],
                "func": self.__enhance_contrast,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            317: {
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "contrast" in query, any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_contrast,
                "args": [float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            318: {
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "contrast" in query, any_in_str(["factor", "divided"], query)],
                "func": self.__enhance_contrast,
                "args": [1/float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            319: { # Default increase contrast - 2x
                "conditions": [has_image_target, any_in_str(["enchance", "improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "contrast" in query],
                "func": self.__enhance_contrast,
                "args": [2],
            },
            320: { # Default decrease contrast - 1/2x
                "conditions": [has_image_target, any_in_str(["disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), "contrast" in query],
                "func": self.__enhance_contrast,
                "args": [1/2],
            },
            321: { # BRIGHTNESS enhance with factor
                "conditions": [has_image_target, any_in_str(["brighten", "lighten", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), any_in_str(["dark", "light", "bright", "dim"], query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_brightness,
                "args": [1 + float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            322: {
                "conditions": [has_image_target, any_in_str(["brighten", "lighten", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), any_in_str(["dark", "light", "bright", "dim"], query), any_in_str(["factor", "times", "points"], query)],
                "func": self.__enhance_brightness,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            323: {
                "conditions": [has_image_target, any_in_str(["darken", "dim", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["dark", "light", "bright", "dim"], query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_brightness,
                "args": [float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            324: {
                "conditions": [has_image_target, any_in_str(["darken", "dim", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["dark", "light", "bright", "dim"], query), any_in_str(["factor", "divided"], query)],
                "func": self.__enhance_brightness,
                "args": [1/float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            325: { # Default increase brightness - 2x
                "conditions": [has_image_target, any_in_str(["brighten", "lighten", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), any_in_str(["dark", "light", "bright", "dim"], query)],
                "func": self.__enhance_brightness,
                "args": [2],
            },
            326: { # Default decrease brightness - 1/2x
                "conditions": [has_image_target, any_in_str(["darken", "dim", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["dark", "light", "bright", "dim"], query)],
                "func": self.__enhance_brightness,
                "args": [1/2],
            },
            315: { # SHARPNESS enhance with factor
                "conditions": [has_image_target, any_in_str(["sharpen", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), any_in_str(["smooth", "sharp"], query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_brightness,
                "args": [1 + float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            327: {
                "conditions": [has_image_target, any_in_str(["sharpen", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), any_in_str(["smooth", "sharp"], query), any_in_str(["factor", "times", "points"], query)],
                "func": self.__enhance_sharpness,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            328: {
                "conditions": [has_image_target, any_in_str(["smooth", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["smooth", "sharp"], query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__enhance_sharpness,
                "args": [float(x)/100 for x in re.compile(r'([0-9]+)').findall(query)],
            },
            329: {
                "conditions": [any_in_str(["smooth", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["smooth", "sharp"], query), any_in_str(["factor", "divided"], query)],
                "func": self.__enhance_sharpness,
                "args": [1/float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            330: { # Default increase sharpness - 2x
                "conditions": [has_image_target, any_in_str(["sharpen", "enchance","improve", "heighten", "increase", "increment", "upgrade", "raise", "lift", "elevate", "touch up", "turn up"], query), "sharp" in query],
                "func": self.__enhance_sharpness,
                "args": [2],
            },
            331: { # Default decrease sharpness - 1/2x
                "conditions": [has_image_target, any_in_str(["smooth", "disenhance", "dehance", "lessen", "decrease", "decrement", "downgrade", "lower", "put down", "cutback", "drop", "turn down", "reduce", "shrink"], query), any_in_str(["smooth", "sharp"], query)],
                "func": self.__enhance_sharpness,
                "args": [1/2],
            },
            332: { # Invert
                "conditions": [has_image_target, any_in_str(["invert", "inverse"], query)],
                "func": self.__invert,
                "args": [],
            },

            # Rotation
            400: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "left" in query or "counter" in query, "degree" in query],
                "func": self.__rotate_counterclockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            401: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "left" in query or "counter" in query, "degree" not in query],
                "func": self.__rotate_counterclockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            500: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "right" in query or "clockwise" in query, "degree" in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            501: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "right" in query or "clockwise" in query, "degree" not in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            600: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "degree" in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            601: {
                "conditions": [has_image_target, "rotate" in query or "turn" in query, "degree" not in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },

            # Filters
            700: {
                "conditions": [has_image_target, "blur" in query],
                "func": self.__blur,
                "args": [],
            },
            800: {
                "conditions": [has_image_target, "sharpen" in query],
                "func": self.__sharpen,
                "args": [],
            },
            900: {
                "conditions": [has_image_target, "smooth" in query],
                "func": self.__smooth,
                "args": [],
            },
            901: {
                "conditions": [has_image_target, "contour" in query],
                "func": self.__contour,
                "args": [],
            },
            902: {
                "conditions": [has_image_target, "detail" in query],
                "func": self.__detail,
                "args": [],
            },
            903: {
                "conditions": [has_image_target, "emboss" in query],
                "func": self.__emboss,
                "args": [],
            },
            904: {
                "conditions": [has_image_target, "enhance" in query, "edge" in query],
                "func": self.__enhance_edges,
                "args": [],
            },
            905: {
                "conditions": [has_image_target, "find" in query, "edge" in query],
                "func": self.__find_edges,
                "args": [],
            },

            # Flip
            906: {
                "conditions": [has_image_target, "mirror" in query],
                "func": self.__mirror,
                "args": [],
            },
            1000: {
                "conditions": [has_image_target, any_in_str(["flip", "flop", "swap", "turn"], query), any_in_str(["horizon", "x", "left", "right"], query)],
                "func": self.__flip_h,
                "args": [],
            },
            1001: {
                "conditions": [has_image_target, any_in_str(["flip", "flop", "swap", "turn"], query), any_in_str(["vertical", "y", "top", "bottom", "up", "down"], query)],
                "func": self.__flip_v,
                "args": [],
            },

            # Mask
            1002: {
                "conditions": [has_image_target, any_in_str(["mask", "cover", "overlay", "fit", "cast", "cut"], query), any_in_str(["circle", "ellipse", "disk", "round"], query)],
                "func": self.__circle_mask,
                "args": [1],
            },
        }

        current_application = command_utils.plugins["aria_core_context"].current_application
        localized_name = current_application.localized_name if current_application is not None else ""

        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if ("these" in query or "this" in query) and "Finder" in current_application:
                    key += 10000
                elif "Finder" in localized_name and len(command_utils.plugins["aria_core_context"].get_selected_items()) > 0:
                    key += 5000
                elif self.check_for_img_target(query) and not "Finder" in localized_name:
                    key += 1000
                elif "Finder" in localized_name and self.check_for_img_target(query):
                    pass
                else:
                    # Finder isn't open, no file ref provided --> give this to another command to handle
                    return 0


                if get_tuple:
                    return (key, query_type)
                return key
        return 0

    def get_template(self, new_cmd_name):
        print("Enter base command and args: ")
        cmd_new = input()

        query_length = len(new_cmd_name)+1

        template = {
            'command': str(cmd_new.split(" ")),
        }

        return template

command = ImgCmd()