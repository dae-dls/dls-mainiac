import signal
import psutil

# Use standard logging in this module.
import logging
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
def find_duplicate_commandlines(this_process=None):
    """
    Return list of psutil.Process objects of a duplicate commandlines.
    Match includes all command line arguments.
    """

    if this_process is None:
        this_process = psutil.Process()

    this_info = this_process.as_dict()

    process_list = []
    for that_process in psutil.process_iter(["pid", "cmdline"]):
        if that_process.info["pid"] == this_info["pid"]:
            continue

        if that_process.info["cmdline"] == this_info["cmdline"]:
            process_list.append(that_process)

    return process_list
  
# ----------------------------------------------------------------
def interrupt_duplicate_commandlines(this_process=None):
    """
    Send interrupt, aka sigint, aka ^C, to all duplicate commandlines, if any are running.
    Match includes all command line arguments.
    """

    process_list = find_duplicate_commandlines(this_process=this_process)

    for process in process_list:
        pid = process.send_signal(signal.SIGINT)
