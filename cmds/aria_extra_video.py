import re, math
from moviepy.editor import *

from ariautils import command_utils, io_utils
from ariautils.misc_utils import any_in_str

class VideoCmd(command_utils.Command):
    info = {
        "title": "Video Management for Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras/",
        'id': "aria_extra_video",
        "version": "1.0.0",
        "description": """
            This command offers various video file management and manipulation functionalities supported by Aria's contextual awareness.
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

        selected_items = None
        try:
            selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
        except:
            io_utils.dprint("Unable to obtain selected items durign aria_extra_video execution")

        if query_type[0] in [5010, 5011, 5012, 10010, 10011, 10012]:
            # Multivideo Methods
            if selected_items != None:
                path = selected_items[0]
                path = path[0:len(path)-path[::-1].index(".")-1] + "_generated.mp4" 
                self.__new_video_file(path, query_type[1]["func"], [VideoFileClip(item.url) for item in selected_items])

        elif query_type[0] in [5050, 10050]:
            # Audio replacement
            if selected_items != None:
                audio_file = self.path_from_str(query)
                for item in selected_items:
                    self.__operate_in_place(item.url, query_type[1]["func"], [AudioFileClip(audio_file)])
            
        elif query_type[0] == 100:
            pass

        elif query_type[0] == 101:
            pass

        elif query_type[0] >= 5000:
            # Operate on selected files in Finder
            if selected_items != None:
                for item in selected_items:
                    self.__operate_in_place(item, query_type[1]["func"], query_type[1]["args"])


    def path_from_str(self, string):
        first_slash = string.index("/")
        file_ext = len(string) - string[::-1].index(".") + 3
        return string[first_slash:file_ext]

    # I/O
    def __operate_in_place(self, path, operation, args):
        if path.startswith("file://"):
            path = path.replace("file://", "")
        path = path.replace("%20", " ")

        video = VideoFileClip(path)
        video = operation(video, *args)

        path = path[0:len(path)-4] + "__" + path[len(path)-4:]

        try:
            video.write_videofile(path)
            io_utils.sprint("Operation complete.")
        except:
            try:
                video.write_videofile(path, codec = 'libx264')
                io_utils.sprint("Operation complete.")
            except:
                io_utils.dprint("Unable to export movie file.")


    def __new_video_file(self, path, operation, videos):
        new_video = operation(videos)
        new_video.write_videofile(path)
        io_utils.sprint("Export complete.")

    def __export_all_frames(self, video = None, path = None):
        if video == None and path != None:
            video = VideoFileClip(path)
        if path == None:
            path = "./docs/exported_frame%04d.png"
        else:
            path = path[0:len(path)-path[::-1].index(".")-1] + "exported_frame%04d.png" 
        video.write_images_sequence(path)

    def __to_gif(self, video = None, path = None):
        if video == None and path != None:
            video = VideoFileClip(path)
        if path == None:
            path = "./docs/exported_gif%04d.gif"
        else:
            path = path[0:len(path)-path[::-1].index(".")-1] + "exported_gif%04d.gif" 
        video.write_gif(path)

    # Multivideo Methods
    def __concat(self, videos):
        io_utils.sprint("Concatenating...")
        return concatenate_videoclips(videos)

    def __grid(self, videos):
        num_vids = len(videos)
        
        root = math.sqrt(num_vids)
        while not root.is_integer():
            num_vids -= 1
            root = math.sqrt(num_vids)

        root = int(root)

        clips = []
        for row in range(root):
            partial = []
            for col in range(root):
                index = root * row + col
                partial.append(videos[index])
            clips.append(partial)
        return clips_array(clips)

    def __overlay(self, videos):
        return CompositeVideoClip(videos)


    # Frame manipulation
    def __resize(self, video, new_width, new_height, _args = []):
        return video.fx(vfx.resize, width = new_width, height = new_height)

    def __set_brightness(self, video, brightness, _args = []):
        return video.fx(vfx.colorx, brightness)

    def __desaturate(self, video, _args = []):
        return video.fx(vfx.blackwhite)

    def __invert(self, video, _args = []):
        return video.fx(vfx.invert_colors)

    def __border(self, video, border_width, color = (255, 255, 255), _args = []):
        return video.fx(vfx.margin, mar = border_width, color = color)

    def __set_opacity(self, video, opacity = 1, _args = []):
        return video.set_opacity(opacity)

    # Fade
    def __fade_in(self, video, duration = 2, color = (0, 0, 0), _args = []):
        io_utils.sprint("Adding fade in...")
        return video.fx(vfx.fadein, duration = duration, color = color)

    def __fade_out(self, audio, duration = 2, color = (0, 0, 0), _args = []):
        io_utils.sprint("Adding fade out...")
        return video.fx(vfx.fadeout, duration = duration, color = color)
    

    # Flipping
    def __flip_h(self, video, _args = []):
        io_utils.sprint("Flipping video horizontally...")
        return video.fx(vfx.mirror_x)

    def __flip_v(self, image, _args = []):
        io_utils.sprint("Flipping video vertically...")
        return video.fx(vfx.mirror_y)

    # Rotation
    def __rotate_clockwise(self, video, angle, _args = []):
        io_utils.sprint("Rotating video clockswise...")
        return video.fx(vfx.rotate, -angle)

    def __rotate_counterclockwise(self, video, counterclock_angle, _args = []):
        io_utils.sprint("Rotating video counterclockwise...")
        return video.fx(vfx.rotate, counterclock_angle)

    # Timing
    def __set_speed(self, video, speed, _args = []):
        return video.fx(vfx.speedx, speed)

    def __set_duration(self, video, duration, _args = []):
        return video.set_duration(duration)

    def __set_fps(self, video, fps, _args = []):
        return video.set_fps(fps)

    def __reverse(self, video, _args = []):
        io_utils.sprint("Reversing video...")
        return video.fx(vfx.reverse)

    # Audio
    def __strip_audio(self, video, _args = []):
        return video.without_audio()

    def __replace_audio(self, video, audio, _args = []):
        old_duration = video.duration
        return video.set_audio(audio).set_duration(old_duration)

    def check_for_video_target(self, string):
        return any_in_str([".mov", ".mp4", ".wemb", ".f4v", ".gif", ".ogg", ".gifv", ".avi", ".qt", ".wmv", ".amv", ".m4p", ".m4v", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".m2v", ".flv"], string.lower())

    def get_query_type(self, query, get_tuple = False):
        parts = query.split()

        selected_items = command_utils.plugins["aria_core_context"].get_selected_items()
        has_video_target = self.check_for_video_target(query)

        if selected_items != None:
            if not has_video_target:
                for item in selected_items:
                    if self.check_for_video_target(item.url):
                        has_video_target = True
                        break

        __query_type_map = {
            # Multivideo Methods
            10: { # Concatenate
                "conditions": [has_video_target, any_in_str(["concat", "join", "append", "splice", "connect", "add", "combine"], query)],
                "func": self.__concat,
                "args": [],
            },
            11: { # Grid
                "conditions": [has_video_target, any_in_str(["make", "create", "construct", "compose", "craft", "form", "generate"], query), any_in_str(["grid", "lattice", "matrix", "array", "mosaic"], query)],
                "func": self.__grid,
                "args": [],
            },
            12: { # Overlay
                "conditions": [has_video_target, any_in_str(["stack", "overlay", "pile", "encrust"], query)],
                "func": self.__overlay,
                "args": [],
            },
            50: { # Replace Audio
                "conditions": [has_video_target, any_in_str(["replace", "override", "insert", "supplant", "substitude", "swap", "switch", "change"], query), any_in_str(["audio", "sound", "noise", "track", "music"], query), any_in_str(["with", "in place", "replac", "instead", "for", "using", "of"], query)],
                "func": self.__replace_audio,
                "args": [],
            },

            100: { # Gif
                "conditions": [has_video_target, any_in_str(["export", "generate", "create", "send", "save", "make", "turn"], query), "gif" in query],
                "func": self.__to_gif,
                "args": [],
            },
            101: { # Export frames
                "conditions": [has_video_target, any_in_str(["export", "save", "extract"], query), any_in_str(["all", "every", "each"], query) or ("the" in query and "frames" in query), any_in_str(["frame", "image", "slide", "tick", "pic", "sample"], query)],
                "func": self.__export_all_frames,
                "args": [],
            },
            
            200: { # Reverse 
                "conditions": [has_video_target, "reverse" in query or (any_in_str(["flip", "swap"], query) and "start" in query and "end" in query)],
                "func": self.__reverse,
                "args": [],
            },
            201: { # Strip audio 
                "conditions": [has_video_target, any_in_str(["remove", "rid", "detach", "strip", "separate", "cut", "erase"], query), any_in_str(["sound", "noise", "audio", "track", "separate"], query)],
                "func": self.__strip_audio,
                "args": [],
            },
            202: { # Desaturate - 'Remove color'
                "conditions": [has_video_target, any_in_str(["remove", "strip", "erase"], query), any_in_str(["color", "hue", "value", "tint"], query), any_in_str(["of", "from", "in", "for"], query)],
                "func": self.__desaturate,
                "args": [],
            },
            203: { # Desaturate - 'Make this desaturated'
                "conditions": [has_video_target, any_in_str(["set", "modify", "alter", "change", "mutate", "make", "adjust"], query), any_in_str(["color", "hue", "value", "tint"], query), any_in_str(["of", "from", "in", "for"], query), any_in_str(["colorless", "desaturated", "grayscale", "black", "white", "mono"], query)],
                "func": self.__desaturate,
                "args": [],
            },
            204: { # Invert colors
                "conditions": [has_video_target, any_in_str(["invert", "inverse", "transplace"], query), any_in_str(["color", "hue", "pixel"], query)],
                "func": self.__invert,
                "args": [],
            },

            # Rotation
            300: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "left" in query or "counter" in query, "degree" in query],
                "func": self.__rotate_counterclockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            301: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "left" in query or "counter" in query, "degree" not in query],
                "func": self.__rotate_counterclockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            302: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "right" in query or "clockwise" in query, "degree" in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            303: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "right" in query or "clockwise" in query, "degree" not in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            304: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "degree" in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            305: {
                "conditions": [has_video_target, "rotate" in query or "turn" in query, "degree" not in query],
                "func": self.__rotate_clockwise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },

            # Border
            400: { # Border with color
                "conditions": [has_video_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge", "margin", "padding"], query) or ("spac" in query and "around" in query), any_in_str(["of", "with", "px", "pixel", "spacing"], query), "color" in query],
                "func": self.__border,
                "args": re.compile(r'(?:color of |add a )([0-9]+|.*)').findall(query),
            },
            401: { # Border with width
                "conditions": [has_video_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge", "margin", "padding"], query) or ("spac" in query and "around" in query), any_in_str(["of", "px", "pixel", "spacing"], query)],
                "func": self.__border,
                "args": re.compile(r'([0-9]+)').findall(query),
            },
            402: { # Default border - 10 pixels
                "conditions": [has_video_target, any_in_str(["add", "give", "put", "attach", "affix", "surround", "bound", "enclose"], query), any_in_str(["border", "edge", "margin", "padding"], query) or ("spac" in query and "around" in query)],
                "func": self.__border,
                "args": [10],
            },

            # Setters
            500: { # Speed
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "increase", "hasten", "fasten", "faster", "increment", "raise", "slow", "decrease", "low", "decrement", "lessen", "reduce", "drop", "speed"], query) or ("speed" in query and "up" in query) or ("speed" in query and "down" in query), any_in_str(["factor", "point", "multipl", "times", "x ", "notch"], query)],
                "func": self.__set_speed,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            501: { # Duration
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "make", "decrease", "increase", "reduce", "raise"], query), any_in_str(["duration", "length", "timing", "span", "time", "period", "timeframe", "playtime"], query), any_in_str(["to", "than", "below", "above"], query), "sec" in query],
                "func": self.__set_duration,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            502: { # FPS
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "make", "decrease", "increase", "reduce", "raise"], query), any_in_str(["framerate", "fps", "frames", "sample", "ticks", "tps"], query), any_in_str(["to", "than", "below", "above"], query)],
                "func": self.__set_fps,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            600: { # Brightness
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "make", "decrease", "increase", "reduce", "raise"], query), any_in_str(["bright", "light", "lumin", "brillianc", "radiance"], query), any_in_str(["to", "than", "below", "above"], query)],
                "func": self.__set_brightness,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            503: { # Opacity
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "make", "decrease", "increase", "reduce", "raise"], query), any_in_str(["opacity", "translucen", "opaque", "transparen"], query), any_in_str(["to", "than", "below", "above"], query)],
                "func": self.__set_opacity,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            504: { # Size
                "conditions": [has_video_target, any_in_str(["adjust", "change", "alter", "set", "modify", "make", "size", "scale"], query), any_in_str(["width", "wide", "horizontal", "dimension", "x-", "w-"], query), any_in_str([" by ", " x ", " times ", "of", "and"], query), any_in_str(["height", "vertically", " y ", "y-", "h-", "tall"], query)],
                "func": self.__resize,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },

            # Fade
            600: { # Set fade in duration
                "conditions": [has_video_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "in" in query) or ("fade" in query and any_in_str(["start", "front", "begin", "head", "first", "open"], query)), "sec" in query],
                "func": self.__fade_in,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            601: { # Set fade out duration
                "conditions": [has_video_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "out" in query) or ("fade" in query and any_in_str(["end", "finish", "tail", "complet", "clos", "last"], query)), "sec" in query],
                "func": self.__fade_out,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            602: { # 3 sec fade in
                "conditions": [has_video_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "in" in query) or ("fade" in query and any_in_str(["start", "front", "begin", "head", "first", "open"], query))],
                "func": self.__fade_in,
                "args": [3]
            },
            603: { # 3 sec fade out
                "conditions": [has_video_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "out" in query) or ("fade" in query and any_in_str(["end", "finish", "tail", "complet", "clos", "last"], query))],
                "func": self.__fade_out,
                "args": [3]
            },

            # Flip
            700: {
                "conditions": [has_video_target, any_in_str(["flip", "flop", "swap", "turn"], query), any_in_str(["horizon", "x", "left", "right"], query)],
                "func": self.__flip_h,
                "args": [],
            },
            701: {
                "conditions": [has_video_target, any_in_str(["flip", "flop", "swap", "turn"], query), any_in_str(["vertical", "y", "top", "bottom", "up", "down"], query)],
                "func": self.__flip_v,
                "args": [],
            },
        }

        current_application = command_utils.plugins["aria_core_context"].current_application
        localized_name = current_application.localized_name if current_application is not None else ""

        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if ("these" in query or "this" in query) and "Finder" in localized_name:
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

command = VideoCmd()