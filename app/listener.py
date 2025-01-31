from .announcer import Announcer
from .display import SystemTrayIcon
from .keyboard import keyboard, KEYCODE

import pygame as pg

import logging
logger = logging.getLogger(__name__)


class Listener:
    def __init__(self, name: str, announcer: Announcer) -> None:
        self.announcer = announcer
        self.icon = SystemTrayIcon(name)
    
    def spin(self):
        logger.info("Entering spin()")
        try:
            self.icon.run()
        finally:
            logger.debug("Exiting spin().")
            self.icon.stop()
    
    def start(self):
        pg.init()
        pg.event.set_blocked(None)
        keyboard.hook_key(KEYCODE.LANG3, self.announcer.notify_user)
        keyboard.hook_key(KEYCODE.LANG4, self.announcer.notify_all)
        keyboard.hook_key(KEYCODE.ESC, self.announcer.acknowledge)
    
    def shutdown(self):
        logger.debug("Shutting down.")
        self.announcer.overlay.hide()
        pg.quit()
        keyboard.unhook_all()
