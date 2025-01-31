# cspell:disable

import os.path, sys


AUDIO_FILE_NAME = "announcement.wav"

if getattr(sys, 'frozen', False):
    AUDIO_FILE = os.path.join(sys._MEIPASS, AUDIO_FILE_NAME)
else:
    AUDIO_FILE = AUDIO_FILE_NAME


class KEYCODE:
    ESC = 1
    F13 = 100
    F14 = 101
    F15 = 102
    F16 = 103
    STOP_MEDIA = -178
    LANG3 = 120
    LANG4 = 119

