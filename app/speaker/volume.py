# cspell:disable

import comtypes
from ctypes import POINTER, cast
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator, EDataFlow, ERole
from pycaw.constants import CLSID_MMDeviceEnumerator

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
    def __init__(self, device):
        interface = device.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        self._volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    @property
    def percent(self) -> float:
        return 100 * self._volume.GetMasterVolumeLevelScalar()
    
    def set_percent(self, percent):
        clamped_percent = max(0, min(percent, 100))
        self._volume.SetMasterVolumeLevelScalar(0.01*clamped_percent, None)
    
    @property
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


class SpeakerVolumeController(VolumeController):
    def __init__(self, search_string: str = "Speaker"):
        speaker = MyAudioUtilities.GetSpeaker(search_string)
        super().__init__(speaker)

