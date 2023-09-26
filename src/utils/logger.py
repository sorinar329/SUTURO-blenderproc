import logging
import time


class Logger:
    def __init__(self):
        logging.basicConfig(filename='logfile.log', level=logging.INFO)
        self.start_time = time.time()

    def log_component(self, iteration: int, component: str):
        elapsed_time = time.time() - self.start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        duration = f"{hours}:{minutes}:{seconds}"
        logging.info(f'At iteration {iteration} for component: ({component}) '
                     f'time elapsed: {duration}')
