from .volume import SpeakerVolumeController
from .player import AudioPlayer

class SpeakerController:
    def __init__(self, search_string: str = "Speaker"):
        self.volume = SpeakerVolumeController(search_string)
        self.player = AudioPlayer(search_string)
    
    def play(self, filename):
        was_muted = self.volume.is_muted
        og_volume = self.volume.percent
        self.volume.set_percent(4)
        self.volume.unmute()
        self.player.play(filename)
        self.volume.set_percent(og_volume)
        self.volume.toggle_mute(was_muted)
