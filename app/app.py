from .listener import Listener
from .announcer import Announcer
from .display import DEFAULT


class ProductivitySuspensionSystem(Listener):
    def __init__(self, audio_filename: str, display:int=None, msg:str=None, font_size:int=None, name=DEFAULT.NAME):
        announcer = Announcer(audio_filename, display, msg, font_size)
        super().__init__(name, announcer)
    

