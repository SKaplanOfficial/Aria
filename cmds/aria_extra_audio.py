import re, os
from pydub import AudioSegment

from pydub.generators import (
    Sine,
    Square,
    Pulse,
    Triangle,
    Sawtooth,
    WhiteNoise,
)

from ariautils.command_utils import Command
from ariautils import context_utils, io_utils
from ariautils.misc_utils import any_in_str

class ImgCmd(Command):
    info = {
        "title": "Audio Management for Aria",
        "repository": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras",
        "documentation_link": "https://github.com/SKaplanOfficial/Aria-Commands/Aria-Extras/",
        'id': "aria_extra_audio",
        "version": "1.0.0",
        "description": """
            This command offers various audio file management and manipulation functionalities supported by Aria's contextual awareness.
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
            selected_items = context_utils.get_selected_items()
            if selected_items != None:
                for item in selected_items:
                    self.__operate_in_place(item, query_type[1]["func"], query_type[1]["args"])

    # I/O
    def __operate_in_place(self, path, operation, args):
        audio = None
        if os.path.isdir(path):
            path = path + "/temp.mp3"
            audio = self.__blank_audio(10)
        elif not self.check_for_audio_target(path):
            # Set path to parent folder
            path = path[0:len(path)-path[::-1].index(".")] + "mp3"
            audio = self.__blank_audio(10)
        else:
            audio = AudioSegment.from_file(path)

        audio = operation(audio, *args)

        if isinstance(audio, AudioSegment):
            audio.export(path)
        elif audio is not None:
            audio_out = audio[0]
            path = path[0:len(path)-path[::-1].index(".")] + audio[1]
            audio_out.export(path, format = audio[1])

        io_utils.sprint("Operation complete.")

    def __blank_audio(self, duration = 8):
        return AudioSegment.silent(duration = duration * 1000)

    # Conversion
    def __to_mp3(self, audio, _args = []):
        io_utils.sprint("Converting to mp3...")
        return (audio, "mp3")

    # Volume
    def __boost_volume(self, audio, dB_amount = 2, _args = []):
        io_utils.sprint("Boosting volume...")
        return audio + dB_amount

    def __boost_volume_by_percent(self, audio, percent = 50, _args = []):
        io_utils.sprint("Boosting volume...")
        increase =  abs(audio.max_dBFS * percent / 100)
        print(audio.max_dBFS)
        print("---", increase)
        return audio + increase

    def __reduce_volume(self, audio, dB_amount = 2, _args = []):
        io_utils.sprint("Reducing volume...")
        return audio - dB_amount

    def __reduce_volume_by_percent(self, audio, percent = 50, _args = []):
        io_utils.sprint("Reducing volume...")
        decrease =  abs(audio.max_dBFS * percent / 100)
        return audio - decrease


    # Fade
    def __fade_in(self, audio, duration = 2, _args = []):
        io_utils.sprint("Adding fade in...")
        return audio.fade_in(int(duration * 1000))

    def __fade_out(self, audio, duration = 2, _args = []):
        io_utils.sprint("Adding fade out...")
        return audio.fade_out(int(duration * 1000))


    # Speed
    def __speedup(self, audio, factor = 1.5, _args = []):
        io_utils.sprint("Speeding up...")
        return audio.speedup(factor)

    def __slowdown(self, audio, factor = 0.5, _args = []):
        io_utils.sprint("Slowing down...")
        return audio.set_frame_rate(audio.frame_rate * factor)

    # Track Adjustments
    def __reverse(self, audio, _args = []):
        io_utils.sprint("Reversing...")
        return audio.reverse()

    def __set_frame_rate(self, audio, new_rate = 100, _args = []):
        io_utils.sprint("Setting frame rate...")
        return audio.set_frame_rate(new_rate)

    def __normalize(self, audio, headroom = 0.1, _args = []):
        io_utils.sprint("Normalizing...")
        return audio.normalize(headroom)

    # Filters
    def __remove_silence(self, audio, _args = []):
        io_utils.sprint("Removing silence...")
        return audio.strip_silence()

    def __low_pass(self, audio, cutoff = 100, _args = []):
        io_utils.sprint("Smooth high-frequency crest...")
        return audio.low_pass_filter(cutoff)

    def __high_pass(self, audio, cutoff = 100, _args = []):
        io_utils.sprint("Smoothing low-freuqnecy troughs...")
        return audio.high_pass_filter(cutoff)


    # Generate Sound
    def __sine(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating sine audio...")
        return Sine(freq).to_audio_segment(duration = duration * 1000)

    def __square(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating square audio...")
        return Square(freq).to_audio_segment(duration = duration * 1000)

    def __triangle(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating triangle audio...")
        return Triangle(freq).to_audio_segment(duration = duration * 1000)

    def __pulse(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating pulse audio...")
        return Pulse(freq).to_audio_segment(duration = duration * 1000)

    def __sawtooth(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating sawtooth audio...")
        return Sawtooth(freq).to_audio_segment(duration = duration * 1000)

    def __white_noise(self, audio, freq = 440, duration = 8, _args = []):
        io_utils.sprint("Creating white noise audio...")
        return WhiteNoise(freq).to_audio_segment(duration = duration * 1000)

    def check_for_audio_target(self, string):
        return any_in_str([".wav", ".mp3", ".ogg", ".flv", ".mp4", ".wma", ".aac"], string.lower())

    def get_query_type(self, query, get_tuple = False):
        parts = query.split()

        selected_items = context_utils.get_selected_items()
        has_audio_target = self.check_for_audio_target(query)

        if selected_items != None:
            if not has_audio_target:
                for item in selected_items:
                    if self.check_for_audio_target(item):
                        has_audio_target = True
                        break

        __query_type_map = {
            # Conversion
            300: {
                "conditions": [has_audio_target, any_in_str(["convert", "change", "format", "make", "modify", "translate", "turn", "transform", "adapt"], query), "mp3" in query],
                "func": self.__to_mp3,
                "args": [],
            },

            # Volume
            400: {
                "conditions": [has_audio_target, any_in_str(["increase", "boost", "increment", "louder"], query) or ("turn" in query and "up" in query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__boost_volume_by_percent,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            401: {
                "conditions": [has_audio_target, any_in_str(["increase", "boost", "increment", "loud"], query) or ("turn" in query and "up" in query), any_in_str(["factor", "levels", "points", "nothces", "db", "decibel"], query)],
                "func": self.__boost_volume,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            402: {
                "conditions": [has_audio_target, any_in_str(["decrease", "lower", "quiet", "lessen"], query) or ("turn" in query and "down" in query), any_in_str(["%", "percent", "perc"], query)],
                "func": self.__reduce_volume_by_percent,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            403: {
                "conditions": [has_audio_target, any_in_str(["decrease", "lower", "quiet", "lessen"], query) or ("turn" in query and "down" in query), any_in_str(["factor", "divided"], query)],
                "func": self.__reduce_volume,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            404: {
                "conditions": [has_audio_target, any_in_str(["increase", "boost", "increment", "loud"], query) or ("turn" in query and "up" in query)],
                "func": self.__boost_volume_by_percent,
                "args": [50],
            },
            405: {
                "conditions": [has_audio_target, any_in_str(["decrease", "lower", "quiet", "lessen"], query) or ("turn" in query and "down" in query)],
                "func": self.__reduce_volume_by_percent,
                "args": [50],
            },

            # Fade
            500: { # Set fade in duration
                "conditions": [has_audio_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "in" in query) or ("fade" in query and any_in_str(["start", "front", "begin", "head", "first", "open"], query)), "sec" in query],
                "func": self.__fade_in,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            501: { # Set fade out duration
                "conditions": [has_audio_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "out" in query) or ("fade" in query and any_in_str(["end", "finish", "tail", "complet", "clos", "last"], query)), "sec" in query],
                "func": self.__fade_out,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            502: { # 3 sec fade in
                "conditions": [has_audio_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "in" in query) or ("fade" in query and any_in_str(["start", "front", "begin", "head", "first", "open"], query))],
                "func": self.__fade_in,
                "args": [3]
            },
            503: { # 3 sec fade out
                "conditions": [has_audio_target, any_in_str(["fade", "add", "append", "insert", "give", "put"], query), ("fade" in query and "out" in query) or ("fade" in query and any_in_str(["end", "finish", "tail", "complet", "clos", "last"], query))],
                "func": self.__fade_out,
                "args": [3]
            },

            # Speed
            600: { # Set speed increase amount
                "conditions": [has_audio_target, any_in_str(["adjust", "change", "alter", "set", "modify", "increase", "hasten", "fasten", "faster", "increment", "raise"], query) or ("speed" in query and "up" in query), any_in_str(["factor", "point", "multipl", "times", "x ", "notch"], query)],
                "func": self.__speedup,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            601: { # Set speed decrease amount
                "conditions": [has_audio_target, any_in_str(["adjust", "change", "alter", "set", "modify", "decrease", "slower", "lessen", "reduce", "drop", "cut"], query) or ("slow" in query and "down" in query), any_in_str(["factor", "point", "multipl", "times", "x ", "notch"], query)],
                "func": self.__slowdown,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            602: { # 2x speed up
                "conditions": [has_audio_target, any_in_str(["adjust", "change", "alter", "set", "modify", "increase", "hasten", "fasten", "faster", "increment", "raise"], query) or ("speed" in query and "up" in query)],
                "func": self.__speedup,
                "args": [2]
            },
            603: { # 1/2 slow down
                "conditions": [has_audio_target, any_in_str(["adjust", "change", "alter", "set", "modify", "decrease", "slower", "lessen", "reduce", "drop", "cut"], query) or ("slow" in query and "down" in query)],
                "func": self.__slowdown,
                "args": [2]
            },

            # Track Manipulation
            700: {
                "conditions": [has_audio_target, "reverse" in query or (any_in_str(["flip", "swap"], query) and "start" in query and "end" in query)],
                "func": self.__reverse,
                "args": [],
            },
            750: { # Set frame rate
                "conditions": [has_audio_target, any_in_str(["set", "modify", "alter"], query), any_in_str(["rate", "sampling", "frame"], query)],
                "func": self.__set_frame_rate,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            780: { # Normalize
                "conditions": [has_audio_target, "normalize" in query],
                "func": self.__normalize,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },

            # Filters
            800: { # Low pass custom cutoff
                "conditions": [has_audio_target, any_in_str(["filter", "cutoff", "lowpass", "low", "pass", "attenuate", "smooth"], query), any_in_str(["peak", "freq", "sound", "audio", "music", "note", "vol", "hz", "amp", "filter"], query), any_in_str(["above", "past", "beyond", "surpass", "more", "greater", "larger", "higher", "louder", "cutoff", "threshold", "target"], query)],
                "func": self.__low_pass,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            801: { # High pass custom cutoff
                "conditions": [has_audio_target, any_in_str(["filter", "cutoff", "highpass", "high", "pass", "attenuate", "smooth"], query), any_in_str(["troughs", "freq", "sound", "audio", "music", "note", "vol", "hz", "amp", "filter"], query), any_in_str(["below", "under", "beneath", "falling", "less", "small", "low", "quiet", "cutoff", "threshold", "target"], query)],
                "func": self.__high_pass,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            802: { # Low pass cutoff at 100 hz
                "conditions": [has_audio_target, any_in_str(["filter", "cutoff", "lowpass", "low", "pass", "attenuate", "smooth"], query), any_in_str(["peak", "freq", "sound", "audio", "music", "note", "vol", "hz", "amp", "filter"], query)],
                "func": self.__low_pass,
                "args": [100],
            },
            803: { # High pass cutoff at 100 hz
                "conditions": [has_audio_target, any_in_str(["filter", "cutoff", "highpass", "high", "pass", "attenuate", "smooth"], query), any_in_str(["troughs", "freq", "sound", "audio", "music", "note", "vol", "hz", "amp", "filter"], query)],
                "func": self.__high_pass,
                "args": [100],
            },
            850: { # Remove silence
                "conditions": [has_audio_target, any_in_str(["remove", "strip", "take", "elim", "cut", "rid", "delete", "erase", "wipe"], query), any_in_str(["silen", "quiet", "dead", "volumeness", "empty", "blank", "nothing", "still", "unusable", "useless", "soundless"], query)],
                "func": self.__remove_silence,
                "args": []
            },

            # Generators
            1900: { # Sine at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "sin" in query],
                "func": self.__sine,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1901: { # Sine at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "sin" in query],
                "func": self.__sine,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1902: { # Sine at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "sin" in query],
                "func": self.__sine,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1903: { # Sine at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sin" in query],
                "func": self.__sine,
                "args": [440, 8],
            },
            1904: { # Square at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "square" in query],
                "func": self.__square,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1905: { # Square at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "square" in query],
                "func": self.__square,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1906: { # Square at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "square" in query],
                "func": self.__square,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1907: { # Square at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "square" in query],
                "func": self.__square,
                "args": [440, 8],
            },
            1908: { # Triangle at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "triangle" in query],
                "func": self.__triangle,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1909: { # Triangle at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "triangle" in query],
                "func": self.__triangle,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1910: { # Triangle at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "triangle" in query],
                "func": self.__triangle,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1911: { # Triangle at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "triangle" in query],
                "func": self.__triangle,
                "args": [440, 8],
            },
            1912: { # Pulse at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "pulse" in query],
                "func": self.__pulse,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1913: { # Pulse at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "pulse" in query],
                "func": self.__pulse,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1914: { # Pulse at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "pulse" in query],
                "func": self.__pulse,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1915: { # Pulse at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "pulse" in query],
                "func": self.__pulse,
                "args": [440, 8],
            },
            1916: { # Sawtooth at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "sawtooth" in query],
                "func": self.__sawtooth,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1917: { # Sawtooth at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "sawtooth" in query],
                "func": self.__sawtooth,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1918: { # Sawtooth at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "sawtooth" in query],
                "func": self.__sawtooth,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1919: { # Sawtooth at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sawtooth" in query],
                "func": self.__sawtooth,
                "args": [440, 8],
            },

            1920: { # WhiteNoise at custom hz for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "white" in query and "noise" in query],
                "func": self.__white_noise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1921: { # WhiteNoise at custom hz for 8 second default
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), any_in_str(["freq", "hz", "hert", "tone", "cycle"], query), "white" in query and "noise" in query],
                "func": self.__white_noise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)] + [8],
            },
            1922: { # WhiteNoise at 440 hz default for custom duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "sec" in query, "white" in query and "noise" in query],
                "func": self.__white_noise,
                "args": [float(x) for x in re.compile(r'([0-9]+)').findall(query)],
            },
            1923: { # WhiteNoise at default hz and duration
                "conditions": [any_in_str(["create", "make", "generate", "construct", "produce", "build", "develop", "conjure", "spawn", "record"], query), any_in_str(["record", "file", "audio", "sound", "mp3", "wav", "noise"], query), "white" in query and "noise" in query],
                "func": self.__white_noise,
                "args": [440, 8],
            },
        }

        for key, query_type in __query_type_map.items():
            if all(query_type["conditions"]):
                if ("these" in query or "this" in query) and "Finder" in context_utils.current_app:
                    key += 10000
                elif "Finder" in context_utils.current_app and context_utils.get_selected_items() != []:
                    key += 5000
                elif self.check_for_img_target(query) and not "Finder" in context_utils.current_app:
                    key += 1000
                elif "Finder" in context_utils.current_app and self.check_for_img_target(query):
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