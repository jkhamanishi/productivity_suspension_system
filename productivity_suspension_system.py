import logging
from threading import Event, Lock
import os.path, sys
import multiprocessing

import keyboard
import pygame as pg
from win32 import win32gui
import wave
import pyaudio


AUDIO_FILE_NAME = "announcement.wav"


if getattr(sys, 'frozen', False):
    AUDIO_FILE = os.path.join(sys._MEIPASS, AUDIO_FILE_NAME)
else:
    AUDIO_FILE = AUDIO_FILE_NAME


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s]: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.DEBUG
)


class KEYCODE:
    ESC = 1
    F13 = 100
    F14 = 101
    F15 = 102
    F16 = 103
    STOP_MEDIA = -178


class ScreenController:
    MESSAGE = "SOMEBODY WANTS YOUR ATTENTION"
    FONT_SIZE = 100
    DISPLAY = 0  # Monitor/screen index
    
    def __init__(self) -> None:
        self.stop_event = Event()
    
    def request_stop(self):
        self.stop_event.set()
    
    def init_display(self):
        self.stop_event.clear()
        pg.display.init()
        info = pg.display.Info()
        self.surface = pg.display.set_mode((info.current_w, info.current_h), pg.NOFRAME, display=self.DISPLAY)
        self.surface_rect = self.surface.get_rect()
        self.move_window_to_front()
        self.init_text()
    
    def move_window_to_front(self):
        hwnd = pg.display.get_wm_info()['window']
        win32gui.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001)
    
    def init_text(self):
        self.font = pg.font.Font(None, ScreenController.FONT_SIZE)
        self.txt = self.font.render(ScreenController.MESSAGE, True, (255, 0, 0))
        self.rect = self.txt.get_rect(center=self.surface_rect.center)
    
    def destroy_surface(self):
        pg.display.quit()
    
    def clear_surface(self):
        self.surface.fill((0, 0, 0))
    
    def display_text(self):
        self.surface.blit(self.txt, self.rect)
    
    def blink_text(self):
        self.init_display()
        clock = pg.time.Clock()
        text_showing = False
        while not self.stop_event.is_set():
            pg.event.pump()
            if text_showing:
                self.clear_surface()
            else:
                self.display_text()
            pg.display.update(self.rect)
            text_showing = not(text_showing)
            clock.tick(4)
        self.destroy_surface()


class AudioPlayer:
    class Stream:
        CHUNK = 1024
        
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
            data = self._wf.readframes(self.CHUNK)
            if bool(data):
                self._stream.write(data)
                self._write_to_stream()
            return
    
    def __init__(self) -> None:
        self.speaker_index = self.get_speaker_index()
    
    def open(self, filename):
        return AudioPlayer.Stream(filename, self.speaker_index)
    
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


class Announcer:
    def __init__(self) -> None:
        self.screen = ScreenController()
        self.audio = AudioPlayer()
        self.notify_user_lock = Lock()
        self.notify_all_lock = Lock()
    
    @staticmethod
    def stop_media():
        keyboard.send(KEYCODE.STOP_MEDIA)
    
    def acknowledge(self):
        self.screen.request_stop()
        keyboard.remove_hotkey(KEYCODE.ESC)
        self.notify_user_lock.release()
        logger.info("Notification acknowledged.")
    
    def _notify_user(self):
        logger.info("Notifying user.")
        keyboard.add_hotkey(KEYCODE.ESC, self.acknowledge)
        self.stop_media()
        self.screen.blink_text()
    
    def notify_user(self):
        if self.notify_user_lock.acquire(blocking=False):
            keyboard.call_later(self._notify_user)
    
    def _notify_all(self):
        logger.info("Notifying everyone.")
        self.audio.play(AUDIO_FILE)
        self.notify_all_lock.release()
    
    def notify_all(self):
        self.notify_user()
        if self.notify_all_lock.acquire(blocking=False):
            keyboard.call_later(self._notify_all)


class Listener:
    def __init__(self) -> None:
        self.announcer = Announcer()
    
    @staticmethod
    def spin():
        logger.info("Entering spin(), press Ctrl+C to exit.")
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            logger.debug("KeyboardInterrupt received. Exiting spin().")
    
    def start(self):
        pg.init()
        pg.event.set_blocked(None)
        keyboard.add_hotkey(KEYCODE.F13, self.announcer.notify_user)
        keyboard.add_hotkey(KEYCODE.F14, self.announcer.notify_all)
    
    def shutdown(self):
        logger.debug("Shutting down.")
        self.announcer.screen.request_stop()
        pg.quit()
        keyboard.unhook_all_hotkeys()


if __name__ == "__main__":
    multiprocessing.freeze_support()  # for pyinstaller
    
    logger.debug("Starting script")
    listener = Listener()
    
    listener.start()
    listener.spin()
    listener.shutdown()
    