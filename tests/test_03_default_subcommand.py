import pytest
import argparse

# Class under test.
from dls_mainiac_lib.mainiac import Mainiac

# Assertion helpers.
from dls_mainiac_lib.assert_helpers import assert_parse_system_exit
from dls_mainiac_lib.assert_helpers import assert_parse_success

import logging

logger = logging.getLogger(__name__)


class Test_03_default_subcommand:

    # ----------------------------------------------------------------------------------------
    def test_03_default_subcommand(
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
                stderr_contains="error: the following arguments are required: positional1",
            )
            assert_parse_system_exit(
                "U2",
                app,
                ["--unknown", "x"],
                -1,
                stderr_contains="error: unrecognized arguments: --unknown",
            )

            # Subcommand with missing positional.
            assert_parse_system_exit(
                "P1",
                app,
                ["subcommand1", "--keyword2=x"],
                -1,
                stderr_contains="error: the following arguments are required: positional1",
            )
            assert_parse_system_exit(
                "P2",
                app,
                [],
                -1,
                stderr_contains="error: the following arguments are required: positional1",
            )

            # Subcommand with bad keyword.
            assert_parse_system_exit(
                "P3",
                app,
                ["subcommand1", "--unknown", "x"],
                -1,
                stderr_contains="error: unrecognized arguments: --unknown",
            )

            # Good command lines, verbose.
            case = "B1"
            assert_parse_success(case, app, ["--verbose", "subcommand1", "positional1"])
            assert app._args.verbose, case
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 is None, case
            assert app._args.positional1 == "positional1", case

            case = "B2"
            assert_parse_success(case, app, ["subcommand1", "--verbose", "positional1"])
            assert app._args.verbose, case
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 is None, case
            assert app._args.positional1 == "positional1", case

            case = "B3"
            assert_parse_success(case, app, ["subcommand1", "positional1", "--verbose"])
            assert app._args.verbose, case
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 is None, case
            assert app._args.positional1 == "positional1", case

            # Good command lines.
            case = "G1"
            assert_parse_success(case, app, ["subcommand1", "positional1"])
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 is None, case
            assert app._args.positional1 == "positional1", case

            case = "G2"
            assert_parse_success(
                case, app, ["subcommand1", "--keyword1=x", "--verbose", "positional1"]
            )
            assert app._args.verbose, case
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 == "x", case
            assert app._args.positional1 == "positional1", case

            case = "G3"
            assert_parse_success(case, app, ["subcommand2", "positional2"])
            assert app._args.subcommand == "subcommand2", case
            assert app._args.keyword2 is None, case
            assert app._args.positional2 == "positional2", case

            assert_parse_success(
                "G4", app, ["subcommand2", "--keyword2=y", "positional2"]
            )

            # Default subcommand.
            case = "G5"
            assert_parse_success(case, app, ["positional1"])
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 is None, case
            assert app._args.positional1 == "positional1", case

            case = "G6"
            assert_parse_success(case, app, ["--keyword1=x", "positional1"])
            assert app._args.subcommand == "subcommand1", case
            assert app._args.keyword1 == "x", case
            assert app._args.positional1 == "positional1", case

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
    def version(self):
        return "x.y.z"

    # ----------------------------------------------------------
    def about(self):
        return {"url": "/some/good/url", "description": "A good description"}

    # ----------------------------------------------------------
    def build_parser(self, arglist=None):

        # Make a parser.
        parser = argparse.ArgumentParser()

        subparsers = parser.add_subparsers(help="subcommands", dest="subcommand")
        subparsers.required = True

        subparser1 = subparsers.add_parser("subcommand1", help="Subcommand 1.")
        # Add keyword arguments.
        subparser1.add_argument(
            "--keyword1",
        )

        # Add positional arguments.
        subparser1.add_argument(
            type=str,
            dest="positional1",
        )

        subparser2 = subparsers.add_parser("subcommand2", help="Subcommand 2.")
        # Add keyword arguments.
        subparser2.add_argument(
            "--keyword2",
        )

        # Add positional arguments.
        subparser2.add_argument(
            type=str,
            dest="positional2",
        )

        # Return a structure describing the default subcommand.
        return {
            "parser": parser,
            "subcommand_dest": "subcommand",
            "default_subcommand": "subcommand1",
        }
