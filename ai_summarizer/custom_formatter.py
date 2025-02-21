import logging

class CustomFormatter(logging.Formatter):
    # Colores para los diferentes niveles de log
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    # Formato base para los logs
    base_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Formatos específicos para cada nivel de log
    FORMATS = {
        logging.DEBUG: green + base_format + reset,
        logging.INFO: blue + base_format + reset,
        logging.WARNING: yellow + base_format + reset,
        logging.ERROR: red + base_format + reset,
        logging.CRITICAL: bold_red + base_format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.grey + self.base_format + self.reset)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
