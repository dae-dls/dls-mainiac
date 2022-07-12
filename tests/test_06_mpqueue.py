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

            logging.getLogger().handlers = []
            for handler in logging.getLogger().handlers:
                print(f"********** handler is a {type(handler).__name__}")

            # Configure the app from command line arguments.
            app.parse_args_and_configure_logging([])

            print(f"********** app.console_handler is {app.console_handler}")
            print(f"********** app.logfile_handler is {app.logfile_handler}")
            print(f"********** app.mpqueue_handler is {app.mpqueue_handler}")
            # Run the gui wrapped in a try/catch.
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

        self.__count = 1

    # ----------------------------------------------------------
    def _run_in_process(self):
        multiprocessing.current_process().name = "process"

        pad = "-" * 10

        for i in range(0, self.__count):
            logger.info(f"info message{i} {pad}")

        time.sleep(0.5)

    # ----------------------------------------------------------
    def run(self):
        logger.info(f"master pid is {os.getpid()}")
        process = multiprocessing.Process(target=self._run_in_process)
        process.start()
        process.join()

        time.sleep(0.1)

        # Verify we heard all the log entries in the mpqueue.
        print(f"********** self.mpqueue_heard_count {self.mpqueue_heard_count}")
        # assert self.__count + 1 == self.mpqueue_heard_count, "mpqueue_heard_count"

        # for i in range(0, self.__count):
        #     if i == 0:
        #         filename = "logform.log"
        #     else:
        #         filename = f"logform.log.{i}"

        #     filename = f"{self.__logfile_directory}/{filename}"

        #     # Check the logfile did NOT get written.
        #     assert not os.path.exists(filename)

        #     # Check the message is the correct rotation.
        #     message = f"message{5-i}"
        #     with open(filename, "r") as stream:
        #         lines = stream.readlines()
        #         assert len(lines) == 1
        #         assert message in lines[0]

        # assert not os.path.exists(f"{self.__logfile_directory}/logform.5")

    # --------------------------------------------------------------------------
    def configure_logging(self, settings=None):
        """
        Configure runtime logging, override base class.
        Presume that self._args is already set.
        """

        settings = {
            "console": {"enabled": False},
            "logfile": {"enabled": False},
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
