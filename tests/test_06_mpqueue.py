import time
import multiprocessing
import os
import shutil
import pytest
import argparse

# Class under test.
from dls_mainiac_lib.mainiac import Mainiac

# Assertion helpers.
from dls_mainiac_lib.assert_helpers import assert_parse_system_exit
from dls_mainiac_lib.assert_helpers import assert_parse_success

import logging

logger = logging.getLogger(__name__)


class Test_06_mpqueue:

    # ----------------------------------------------------------------------------------------
    def test(
        self,
        constants,
        logging_setup,
        output_directory,
        capsys,
    ):
        """
        Test mainiac base class.
        """

        failure_message = None
        try:

            # Instantiate the app class.
            app = _App()

            # logging.getLogger().handlers = []
            # for handler in logging.getLogger().handlers:
            #    print(f"********** handler is a {type(handler).__name__}")

            # Configure the app from command line arguments.
            app.parse_args_and_configure_logging([])

            # Call the run method of the object, wrapped in a try/catch.
            app.try_run_catch()

        except Exception as exception:
            logger.exception("unexpected exception during the test", exc_info=exception)
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)


# ---------------------------------------------------------------------------------
class _App(Mainiac):
    """
    App class.
    """

    def __init__(
        self,
    ):

        program_name = "test_06_mpqueue"

        self.__logfile_directory = f"/tmp/logs/{program_name}"

        if os.path.isdir(self.__logfile_directory):
            shutil.rmtree(self.__logfile_directory)

        Mainiac.__init__(self, program_name)

        self.__count = 5

    # ----------------------------------------------------------
    def _run_in_process(self, mpqueue):
        multiprocessing.current_process().name = "process"

        # Remove existing handlers.
        logging.getLogger().handlers = []
        mpqueue_handler = logging.handlers.QueueHandler(mpqueue)
        mpqueue_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(mpqueue_handler)

        pad = "-" * 100

        for i in range(0, self.__count):
            logger.info(f"info message{i} {pad}")

    # ----------------------------------------------------------
    def run(self):
        logger.info(f"master pid is {os.getpid()}")
        process = multiprocessing.Process(
            target=self._run_in_process, args=[self.mpqueue]
        )
        process.start()
        process.join()

        time.sleep(0.2)

        # Verify we heard all the log entries in the mpqueue.
        assert self.__count == self.mpqueue_heard_count, "mpqueue_heard_count"

        for i in range(0, self.__count):
            if i == 0:
                filename = "logform.log"
            else:
                filename = f"logform.log.{i}"

            filename = f"{self.__logfile_directory}/{filename}"

            # Check the logfile got written.
            assert os.path.exists(filename), f"{filename} exists"

            # Check the message is the correct rotation.
            message = f"message{self.__count-i-1}"
            with open(filename, "r") as stream:
                lines = stream.readlines()
                assert len(lines) == 1
                if message not in lines[0]:
                    logger.info(
                        f"filename {filename}\n  got {lines[0]}\n  but wanted {message}"
                    )
                assert message in lines[0]

        # assert not os.path.exists(f"{self.__logfile_directory}/logform.5")

    # --------------------------------------------------------------------------
    def configure_logging(self, settings=None):
        """
        Configure runtime logging, override base class.
        Presume that self._args is already set.
        """

        settings = {
            "console": {"enabled": True},
            "logfile": {"enabled": True},
            "max_bytes": 100,
            "mpqueue": {"enabled": True},
        }
        # Call the base method which has the extra kwarg.
        Mainiac.configure_logging(self, settings)

    # ----------------------------------------------------------
    def version(self):
        return "x.y.z"

    # ----------------------------------------------------------
    def about(self):
        return {"url": "/some/good/url", "description": "A good description"}

    # ----------------------------------------------------------
    def build_parser(self, arglist=None):

        # Make a parser.
        parser = argparse.ArgumentParser()

        # Return a structure describing the default subcommand.
        return parser
