import pytest
import argparse

# Class under test.
from dls_mainiac_lib.mainiac import Mainiac

# Assertion helpers.
from dls_mainiac_lib.assert_helpers import assert_parse_system_exit
from dls_mainiac_lib.assert_helpers import assert_parse_success

import logging

logger = logging.getLogger(__name__)


class Test_04_rotating_subcommand:

    # ----------------------------------------------------------------------------------------
    def test_04_rotating_subcommand(
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

            # Configure the app from command line arguments.
            app.parse_args_and_configure_logging([])

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
        Mainiac.__init__(self, "test_02_subcommand")

    # ----------------------------------------------------------
    def run(self):
        logger.info("info message1")
        logger.info("info message2")
        logger.info("info message3")

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