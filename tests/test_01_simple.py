import pytest
import argparse

# Class under test.
from dls_mainiac_lib.mainiac import Mainiac

# Assertion helpers.
from dls_mainiac_lib.assert_helpers import assert_parse_system_exit
from dls_mainiac_lib.assert_helpers import assert_parse_success


import logging

logger = logging.getLogger(__name__)


class Test_01_simple:

    # ----------------------------------------------------------------------------------------
    def test_01_simple(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """
        Test mainiac base class.
        """

        failure_message = None
        try:

            # Instantiate the app class.
            app = _App()

            # Help.
            assert_parse_system_exit(
                "H", app, ["--help"], 0, stdout_contains="positional arguments:"
            )

            # Version.
            assert_parse_system_exit(
                "V1", app, ["--version"], 0, stdout_contains="x.y.z"
            )
            assert_parse_system_exit(
                "V2", app, ["--version", "oops"], 0, stdout_contains="x.y.z"
            )
            assert_parse_system_exit(
                "V3", app, ["oops", "--version"], 0, stdout_contains="x.y.z"
            )

            # About.
            assert_parse_system_exit(
                "A1", app, ["--about"], 0, stdout_contains="/some/good/url"
            )
            assert_parse_system_exit(
                "A3", app, ["--about", "oops"], 0, stdout_contains="/some/good/url"
            )
            assert_parse_system_exit(
                "A2", app, ["oops", "--about"], 0, stdout_contains="/some/good/url"
            )

            # Unknown flags.
            assert_parse_system_exit(
                "U1",
                app,
                ["--unknown"],
                -1,
                stderr_contains="error: the following arguments are required: positional",
            )

            # Missing required positional.
            assert_parse_system_exit(
                "U2",
                app,
                [],
                -1,
                stderr_contains="error: the following arguments are required: positional",
            )

            # Too many positionals.
            assert_parse_system_exit(
                "T1",
                app,
                ["a", "b"],
                -1,
                stderr_contains="error: unrecognized arguments: b",
            )

            # Good command line.
            assert_parse_success("G1", app, ["positional1"])
            assert app._args.positional == "positional1"

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
        Mainiac.__init__(self, "test_01_simple")

    # ----------------------------------------------------------
    def version(self):
        """
        Method called from mainiac command line parsing.
        Should return string in form of N.N.N.
        """
        return "x.y.z"

    # ----------------------------------------------------------
    def about(self):
        """
        Method called from mainiac command line parsing.
        Should return dict which can be serialized by json.
        """

        return {"url": "/some/good/url", "description": "A good description"}

    # ----------------------------------------------------------
    def build_parser(self, arglist=None):
        """
        Method called from mainiac command line parsing.
        Should return argparser for this program.
        """

        # Make a parser.
        parser = argparse.ArgumentParser()

        # Add keyword arguments.
        parser.add_argument(
            "--keyword",
        )

        # Add positional arguments.
        parser.add_argument(
            type=str,
            dest="positional",
        )

        return parser
