from .speaker import SpeakerController
from .display import ScreenOverlay
from .keyboard import keyboard, KEYCODE

from threading import Lock


import logging
logger = logging.getLogger(__name__)


class Announcer:
    def __init__(self, audio_filename: str, display:int=None, msg:str=None, font_size:int=None) -> None:
        self.audio_filename = audio_filename
        self.overlay = ScreenOverlay(display, msg, font_size)
        self.audio = SpeakerController()
        self.notify_user_lock = Lock()
        self.notify_all_lock = Lock()
    
    @staticmethod
    def stop_media():
        keyboard.send(KEYCODE.STOP_MEDIA)
    
    def _acknowledge(self):
        self.overlay.hide()
        if self.notify_user_lock.locked():
            self.notify_user_lock.release()
            logger.info("Notification acknowledged.")
    
    def acknowledge(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            keyboard.call_later(self._acknowledge)
    
    def _notify_user(self):
        logger.info("Notifying user.")
        self.stop_media()
        self.overlay.show()
    
    def notify_user(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            logger.debug("Notify user request received.")
            if self.notify_user_lock.acquire(blocking=False):
                keyboard.call_later(self._notify_user)
    
    def _notify_all(self):
        logger.info("Notifying everyone.")
        self.audio.play(self.audio_filename)
        self.notify_all_lock.release()
    
    def notify_all(self, event: keyboard.KeyboardEvent):
        if event.event_type == keyboard.KEY_DOWN:
            logger.debug("Notify all request received.")
            self.notify_user(event)
            if self.notify_all_lock.acquire(blocking=False):
                keyboard.call_later(self._notify_all)
