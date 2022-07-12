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


class Test07GraypySingleproc:

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
            app = _SingleprocApp()

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
class _SingleprocApp(Mainiac):
    """
    App class.
    """

    def __init__(
        self,
    ):

        program_name = "test_graylog"

        Mainiac.__init__(self, program_name)

        self.__count = 2

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

        try:
            raise (RuntimeError("deliberate exception"))
        except Exception as exception:
            logger.error(f"got: {exception}", exc_info=exception)

    # ----------------------------------------------------------
    def run(self):

        pad = "-" * 100

        for i in range(0, self.__count):
            logger.info(f"info message{i} {pad}")

        try:
            raise (RuntimeError("deliberate exception"))
        except Exception as exception:
            logger.error(f"got: {exception}", exc_info=exception)

    # --------------------------------------------------------------------------
    def configure_logging(self, settings=None):
        """
        Configure runtime logging, override base class.
        Presume that self._args is already set.
        """

        settings = {
            "console": {"enabled": True},
            "logfile": {"enabled": False},
            "mpqueue": {"enabled": False},
            "graypy": {
                "enabled": True,
                "host": "172.23.7.128",
                "port": 12201,
                "protocol": "UDP",
            },
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


class Test07GraypyMultiproc:

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
            app = _MultiprocApp()

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
class _MultiprocApp(Mainiac):
    """
    App class.
    """

    def __init__(
        self,
    ):
        multiprocessing.current_process().name = "main_test_process"

        program_name = "main_test_process"

        Mainiac.__init__(self, program_name)

        self.__count = 2

    # ----------------------------------------------------------
    def _run_in_process(self, mpqueue):
        multiprocessing.current_process().name = "new_test_process"

        settings = {
            "console": {"enabled": False},
            "logfile": {"enabled": False},
            "mpqueue": {"enabled": False},
            "graypy": {
                "enabled": True,
                "host": "172.23.7.128",
                "port": 12201,
                "protocol": "UDP",
            },
        }

        # Remove existing handlers.
        logging.getLogger().handlers = []

        my_mainiac = Mainiac("run_in_process")
        my_mainiac.configure_logging(settings)

        pad = "-" * 100

        for i in range(0, self.__count):
            logger.info(f"info message{i} {pad}")

        try:
            raise (RuntimeError("deliberate exception"))
        except Exception as exception:
            logger.error(f"got: {exception}", exc_info=exception)

    # ----------------------------------------------------------
    def run(self):

        # Start a process from which messages will be emitted.
        process = multiprocessing.Process(
            target=self._run_in_process, args=[self.mpqueue]
        )
        process.start()
        process.join()

    # --------------------------------------------------------------------------
    def configure_logging(self, settings=None):
        """
        Configure runtime logging, override base class.
        Presume that self._args is already set.
        """

        settings = {
            "console": {"enabled": False},
            "logfile": {"enabled": False},
            "mpqueue": {"enabled": False},
            "graypy": {
                "enabled": True,
                "host": "172.23.7.128",
                "port": 12201,
                "protocol": "UDP",
            },
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
