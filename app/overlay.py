from threading import Event
import pygame as pg
from win32 import win32gui


class ScreenOverlay:
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
        self.font = pg.font.Font(None, ScreenOverlay.FONT_SIZE)
        self.txt = self.font.render(ScreenOverlay.MESSAGE, True, (255, 0, 0))
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
    
    def show(self):
        self.blink_text()
    
    def hide(self):
        self.request_stop()
