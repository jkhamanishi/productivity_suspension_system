from .listener import Listener
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s]: %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.INFO
)


if __name__ == "__main__":
    logger.debug("Starting script")
    listener = Listener()
    
    listener.start()
    listener.spin()
    listener.shutdown()
    