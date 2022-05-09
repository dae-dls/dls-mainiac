import os
import multiprocessing
import threading

# Log formatter.
from dls_logging_formatter.dls_logging_formatter import DlsLoggingFormatter

# Python standard logging.
import logging
import logging.handlers


# -------------------------------------------------------------------------
class PermittedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Override of logging class which creates logfiles with writable permissions.
    """

    def _open(self):
        # print("********** PermittedRotatingFileHandler constructor setting umask")
        # Save old umask.
        umask = os.umask(0)
        # Modify to allow all writable.
        os.umask(umask & ~0o0666)
        # Call base class method.
        rtv = logging.handlers.RotatingFileHandler._open(self)
        # Replace old umask.
        os.umask(umask)
        return rtv


# -------------------------------------------------------------------------
class Log666:
    # -------------------------------------------------------------------------
    def start_logfile(program_name, max_bytes=10000000, backup_count=2):
        """
        Start a rotating log in a standard logging directory location.
        """

        multiprocessing.current_process().name = program_name
        threading.current_thread().name = "main"

        # Place log messages in output directory named for this program.
        logfile_directory = "/tmp/logs/%s" % (program_name)

        if not os.path.exists(logfile_directory):
            # Make sure that parent directories which get created will have public permission.
            umask = os.umask(0)
            os.umask(umask & ~0o0777)
            os.makedirs(logfile_directory)
            os.umask(umask)

        logfile_filename = "%s/logging_formatted.log" % (logfile_directory)

        logfile_handler = PermittedRotatingFileHandler(
            logfile_filename, max_bytes, backup_count
        )

        # Let logging write custom formatted messages to stdout.
        logfile_handler.setFormatter(DlsLoggingFormatter())
        logging.getLogger().addHandler(logfile_handler)

        return logfile_handler
