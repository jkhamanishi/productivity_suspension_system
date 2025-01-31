# cspell:disable

import comtypes
from ctypes import POINTER, cast
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator, EDataFlow, ERole
from pycaw.constants import CLSID_MMDeviceEnumerator

import wave
import pyaudio

import logging
logger = logging.getLogger(__name__)


class MyAudioUtilities(AudioUtilities):
    @staticmethod
    def GetDevice(id=None):
        device_enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_INPROC_SERVER)
        if id is not None:
            speaker = device_enumerator.GetDevice(id)
        else:
            speaker = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender.value, ERole.eMultimedia.value)
        return speaker
    
    @staticmethod
    def GetSpeaker(search_string: str):
        mixer_output = None
        device_list = MyAudioUtilities.GetAllDevices()
        for device in device_list:
            if search_string in str(device):
                mixer_output = device
        
        logger.info("Speaker: '%s'" % str(mixer_output))
        
        device_id = mixer_output.id if mixer_output is not None else None
        return MyAudioUtilities.GetDevice(device_id)


class VolumeController:
    def __init__(self, speaker):
        interface = speaker.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        self._volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    def get_percent(self) -> float:
        return 100 * self._volume.GetMasterVolumeLevelScalar()
    
    def set_percent(self, percent):
        clamped_percent = max(0, min(percent, 100))
        self._volume.SetMasterVolumeLevelScalar(0.01*clamped_percent, None)
    
    def is_muted(self) -> bool:
        return self._volume.GetMute()
    
    def toggle_mute(self, mute: bool = None) -> None:
        if mute is not None:
            self._volume.SetMute(mute, None)
        else:
            self._volume.SetMute(not self.is_muted(), None)
    
    def mute(self):
        self.toggle_mute(True)
    
    def unmute(self):
        self.toggle_mute(False)


class Stream:
    CHUNK_SIZE = 1024
    
    def __init__(self, filename, speaker_index): self.open(filename, speaker_index)
    def __enter__(self): return self
    def __exit__(self, *args): self.close()
    
    def open(self, filename, speaker_index):
        self._wf = wave.open(filename, 'rb')
        self._p = pyaudio.PyAudio()
        stream_conf = {
            "rate": self._wf.getframerate(),
            "channels": self._wf.getnchannels(),
            "format": self._p.get_format_from_width(self._wf.getsampwidth()),
            "output": True,
            "output_device_index": speaker_index
        }
        self._stream = self._p.open(**stream_conf)
    
    def close(self):
        self._wf.close()
        self._stream.close()    
        self._p.terminate()
    
    def play(self):
        self._write_to_stream()
    
    def _write_to_stream(self):
        data = self._wf.readframes(self.CHUNK_SIZE)
        if bool(data):
            self._stream.write(data)
            self._write_to_stream()


class AudioPlayer:
    def __init__(self) -> None:
        self.speaker_index = self.get_speaker_index()
    
    def open(self, filename):
        return Stream(filename, self.speaker_index)
    
    def play(self, filename):
        with self.open(filename) as stream:
            stream.play()
    
    @staticmethod
    def get_speaker_index():
        speaker_index = None
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        for i in range(0, info.get('deviceCount')):
            name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            if "Speaker" in name:
                logger.info("Output speaker index: [%d] %s", i, name)
                speaker_index = i
                break
        p.terminate()
        return speaker_index


class AudioController:
    def __init__(self, search_string: str = "Speaker"):
        speaker = MyAudioUtilities.GetSpeaker(search_string)
        self.volume = VolumeController(speaker)
        self.player = AudioPlayer()
    
    def play(self, filename):
        was_muted = self.volume.is_muted()
        og_volume = self.volume.get_percent()
        self.volume.set_percent(100)
        self.volume.unmute()
        self.player.play(filename)
        self.volume.set_percent(og_volume)
        self.volume.toggle_mute(was_muted)
