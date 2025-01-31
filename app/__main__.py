from .app import ProductivitySuspensionSystem, DEFAULT
import argparse
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s]: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.INFO
)


SAMPLE_AUDIO_FILE = "assets/announcement.wav"


def parse_args():
    parser = argparse.ArgumentParser(prog="app")
    parser.add_argument("-f", "--file",    default=SAMPLE_AUDIO_FILE, help="announcement WAV filepath to play", dest='audio_filename')
    parser.add_argument("-d", "--display", default=DEFAULT.DISPLAY, type=int, help="index of the display screen to show announcement", metavar='IDX')
    parser.add_argument("-m", "--msg",     default=DEFAULT.MESSAGE, help="message to display on the screen")
    parser.add_argument("-s", "--size",    default=DEFAULT.FONT_SIZE, type=int, help="font size of the message to display on the screen", dest='font_size')
    parser.add_argument("-n", "--name",    default=DEFAULT.NAME, help="display name for the system tray icon")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    logger.debug("Starting script")
    app = ProductivitySuspensionSystem(**vars(args))
    
    app.start()
    app.spin()
    app.shutdown()
