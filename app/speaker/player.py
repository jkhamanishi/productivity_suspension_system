# cspell:disable

import wave
import pyaudio

import logging
logger = logging.getLogger(__name__)


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
    def __init__(self, search_string: str = "Speaker") -> None:
        self.speaker_index = self.get_speaker_index(search_string)
    
    def open(self, filename):
        return Stream(filename, self.speaker_index)
    
    def play(self, filename):
        with self.open(filename) as stream:
            stream.play()
    
    @staticmethod
    def get_speaker_index(search_string: str):
        speaker_index = None
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        for i in range(0, info.get('deviceCount')):
            name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            if search_string in name:
                logger.info("Output speaker index: [%d] %s", i, name)
                speaker_index = i
                break
        p.terminate()
        return speaker_index

