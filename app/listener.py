from . import KEYCODE
from .announcer import Announcer
from .tray_icon import SystemTrayIcon

import keyboard
import pygame as pg

import logging
logger = logging.getLogger(__name__)

class Listener:
    def __init__(self) -> None:
        self.name = "Productivity Suspension System Interface"
        self.announcer = Announcer()
        self.icon = SystemTrayIcon(self.name)
    
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
