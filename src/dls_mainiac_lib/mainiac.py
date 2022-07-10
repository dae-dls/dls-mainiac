import re
import os
import sys
import json
import random
import argparse
import contextlib
import io
import sys

from string import Template

# Log formatter.
from dls_logform.dls_logform import DlsLogform
from dls_logform.dls_logform import format_exception_causes

# Rotating log file.
from dls_mainiac_lib.log666 import Log666

# Use standard logging in this module.
import logging
import logging.handlers

logger = logging.getLogger(__name__)


class ParserBadSubparser(RuntimeError):
    pass


class ParserOtherExit(RuntimeError):
    pass


@contextlib.contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class Namespace:
    pass


class Mainiac:
    """
    Base class.  Handles details like logging.
    The deriving class must provide two methods: run() and build_parser()
    """

    def __init__(self, program_name):
        self._program_name = program_name

        # Start off with empty args that can be modified by a test program.
        self._args = Namespace()
        self._args.version = False
        self._args.about = False
        self._args.verbose = False

        # Expose handlers as instance attributes.
        self.console_handler = None
        self.logfile_handler = None

    # ----------------------------------------------------------
    def program_name(self, program_name=None):
        """
        Get and optionally set the program name.
        If done before configure_logging, this will form part of the log filename.
        """
        if program_name is not None:
            self._program_name = program_name

        return self._program_name

    # ----------------------------------------------------------
    def try_run_catch(self):
        """
        Run application and handle exception.
        """

        try:
            self.run()
        except KeyboardInterrupt as exception:
            short_message = "%s stopped on keyboard interrupt" % (self._program_name)
            long_message = "%s...\n    %s" % (
                short_message,
                format_exception_causes(exception).replace("... ", "\n    "),
            )

            # User wants verbose?
            if self._args.verbose:
                logger.exception(long_message, exc_info=exception)
            else:
                if self.console_handler is not None:
                    self.console_handler.setLevel(logging.CRITICAL)
                logger.exception(long_message, exc_info=exception)
                print("%s" % short_message)

        except Exception as exception:
            message = "%s %s...\n    %s" % (
                self._program_name,
                self._synonym_of_failed(),
                format_exception_causes(exception).replace("... ", "\n    "),
            )

            # User wants verbose?
            if self._args.verbose:
                logger.exception(message, exc_info=exception)
            else:
                if self.console_handler is not None:
                    self.console_handler.setLevel(logging.CRITICAL)
                logger.exception(message, exc_info=exception)
                print("%s" % message)

    # --------------------------------------------------------------------------
    def _synonym_of_failed(self):
        """
        Return a random synonym for "failed".
        """

        synonyms = [
            "fails",
            "sighs",
            "surrenders",
            "cannot continue",
            "notices a problem",
            "scratches its head",
            "is confused",
            "grinds to a halt",
            "stops unhappily",
            "dies fatally",
            "stops functioning",
            "goes belly up",
            "kicks the bucket",
            "croaks",
            "pleads for help",
            "is lost",
            "displays frowny face",
            "cannot think like that",
        ]

        return synonyms[random.randrange(0, len(synonyms), 1)]

    # --------------------------------------------------------------------------
    def set_arg(self, name, value):
        """
        Set arg value.
        Used by unit tests to set the args as if they we parsed.
        """

        # Set the namespace variable.
        self._args.__dict__.update({name: value})

    # ----------------------------------------------------------
    def add_common_arguments(self, parser):

        parser.add_argument(
            "--version",
            help="Print version as N.N.N and exit.",
            action="store_true",
            dest="version",
        )

        parser.add_argument(
            "--about",
            help="Print information about the program as json, and exit.",
            action="store_true",
            dest="about",
        )

        parser.add_argument(
            "--verbose",
            help="Display more debug.",
            action="store_true",
            dest="verbose",
        )

    # --------------------------------------------------------------------------
    def parse_args_and_configure_logging(self, arglist=None, settings=None):
        """
        Parse command line and configure runtime logging.
        """

        try:
            self.parse_args(arglist)

            self.configure_logging(settings=settings)

        except Exception as exception:
            logger.exception(
                "%s is unable to start" % (self._program_name), exc_info=exception
            )

    # --------------------------------------------------------------------------
    def parse_args(self, arglist=None):
        """
        Parse command line.

        """

        try:
            # Caller not giving arglist?
            if arglist is None:
                arglist = sys.argv[1:]

            # Any arg that looks like a negative scientific notation, put a space before it so it doesn't get treated like a flag.
            # https://stackoverflow.com/questions/9025204/python-argparse-issue-with-optional-arguments-which-are-negative-numbers/17236161
            # The regex looks for:
            # - : a negative sign
            # \\d* : zero or more digits (for oddly formatted values like -.5e-2 or -4354.5e-6)
            # \\.? : an optional period (e.g., -2e-5 is reasonable)
            # \\d* : another set of zero or more digits (for things like -2e-5 and -7.e-3)
            # e : to match the exponent marker
            # re.I makes it match both -2e-5 and -2E-5. Using p.match means that it only searches from the start of each string.
            p = re.compile("-\\d*\\.?\\d*e", re.I)
            # logger.debug("arglist original %s" % (arglist,))
            arglist = [" " + a if p.match(a) else a for a in arglist]
            # logger.debug("arglist treated for negative scientific notation %s" % (arglist,))

            # Make a pre-parser, who does not look for --help.
            pre_parser = argparse.ArgumentParser(add_help=False)

            # Add the flags common to all programs.
            self.add_common_arguments(pre_parser)

            # Parse for the known flags, stripping them out of the arg list.
            pre_args, arglist2 = pre_parser.parse_known_args(args=arglist)

            # Flags indicate this is a version request only?
            if hasattr(pre_args, "version") and pre_args.version:
                print(self.version())
                sys.exit(0)

            # Flags indicate this is an about request only?
            if hasattr(pre_args, "about") and pre_args.about:
                print(json.dumps(self.about(), indent=4))
                sys.exit(0)

            # Call the abstract method in the deriving class to give us a parser.
            # This will give <flags> subcommand <flags and positionals>.
            real_parser = self.build_parser(arglist=arglist2)

            args = None

            # Parser builder returns a dict instead of just an ArgParser?
            if isinstance(real_parser, dict):
                # Use the dict to get subcommand information.
                otherstuff = real_parser
                real_parser = otherstuff["parser"]
                subcommand_dest = otherstuff["subcommand_dest"]
                default_subcommand = otherstuff["default_subcommand"]

                try:
                    # Try the parse and look for a possible missing subcommand name.
                    args = self._try_the_parse(real_parser, arglist2, subcommand_dest)
                except ParserBadSubparser:
                    # Insert the default subcommand in the command line args.
                    arglist2.insert(0, default_subcommand)
                except ParserOtherExit:
                    pass

            # A first pass was not tried or not successful?
            if args is None:
                # Parse again.
                args = real_parser.parse_args(arglist2)

            # Flags indicate verbose debug?
            if hasattr(pre_args, "verbose") and pre_args.verbose:
                args.verbose = True
            else:
                args.verbose = False

            # Keep the args because the run method needs some things not in the config file.
            self._args = args

        except Exception as exception:
            logger.exception("unable to parse arguments", exc_info=exception)
            sys.exit(-1)

    # --------------------------------------------------------------------------
    def _try_the_parse(self, parser, arglist, subcommand_dest):
        """
        Try the parse.
        If fails, analyze the stdout and raise either ParserBadSubparser or ParserOtherExit.
        """

        with captured_output() as (captured_stdout, captured_stderr):
            try:
                args = parser.parse_args(arglist)
                parse_error = False
            except SystemExit:
                parse_error = True

            if parse_error:
                captured_stdout.seek(0)
                captured_stdout = captured_stdout.read()
                captured_stderr.seek(0)
                captured_stderr = captured_stderr.read()

                # if captured_stdout != "":
                #     logger.error("try captured stdout: %s" % (captured_stdout))
                # if captured_stderr != "":
                #     logger.error("try captured stderr: %s" % (captured_stderr))

                if "argument %s: invalid choice" % (subcommand_dest) in captured_stderr:
                    raise ParserBadSubparser()
                elif (
                    "the following arguments are required: %s" % (subcommand_dest)
                    in captured_stderr
                ):
                    raise ParserBadSubparser()
                else:
                    raise ParserOtherExit()

        return args

    # --------------------------------------------------------------------------
    def configure_logging(self, settings=None):
        """
        Configure runtime logging.
        Presume that self._args is already set.
        """

        if settings is None:
            settings = {}

        try:
            # All output throughout the program goes through python logging.
            # If debug_level is given as any value, then all output uses logging formatter at that level.
            # If debug_level is not given, then uses INFO with only the message part.

            # Always output log messages to the console.
            # OBS! Taurus already sets up a console handler.
            console_handler = None
            for handler in logging.getLogger().handlers:
                # TODO: In configure_logging, properly detect existence of an existing Taurus console hander.
                console_handler = handler
                break

            # No handler already?
            if console_handler is None:
                console_handler = logging.StreamHandler()
                logging.getLogger().addHandler(console_handler)

            # Log level for all modules.
            logging.getLogger().setLevel(logging.DEBUG)

            # User wants verbose?
            if hasattr(self._args, "verbose") and self._args.verbose:
                # Let logging write custom formatted messages to stdout, long format.
                formatter = DlsLogform()
                console_handler.setFormatter(formatter)
                # Log level for the console, verbose
                console_handler.setLevel(logging.DEBUG)
            else:
                formatter = DlsLogform(type="bare")
                console_handler.setFormatter(formatter)
                # Log level for the console, not verbose.
                console_handler.setLevel(logging.INFO)

            # Always output log messages to output file named for this bisstis.
            logfile_handler = Log666.start_logfile(self._program_name, settings)

            # File log level.
            logfile_handler.setLevel(logging.DEBUG)

            # Expose handlers instance attributes.
            self.console_handler = console_handler
            self.logfile_handler = logfile_handler

            # Don't show matplotlib font debug.
            # logging.getLogger("matplotlib.font_manager").setLevel("INFO")

        except Exception as exception:
            logger.exception(
                "unable configure logging: %s %s"
                % (type(exception).__name__, str(exception)),
                exc_info=exception,
            )

    # ----------------------------------------------------------------
    def substitute_symbols_in_dict(self, dict, symtable):
        """
        Substitute template variables from symbol table.
        """

        template_string = json.dumps(dict)

        template_string = self.substitute_symbols_in_string(template_string, symtable)

        return json.loads(template_string)

    # ----------------------------------------------------------------
    def substitute_symbols_in_file(self, template_filename, symtable, output_filename):
        """
        Substitute template variables from symbol table and write to output filename.
        """

        with open(template_filename, "rt") as filehandle:
            template_string = filehandle.read()

        template_string = self.substitute_symbols_in_string(template_string, symtable)

        with open(output_filename, "wt") as filehandle:
            filehandle.write(template_string)

    # ----------------------------------------------------------------
    def substitute_symbols_in_string(self, template_string, symtable):
        """
        Substitute template variables from string.
        """

        old_template_string = None
        max_depth = 10
        depth = 0
        while template_string != old_template_string:
            old_template_string = template_string
            template = Template(template_string)
            template_string = template.safe_substitute(symtable)
            depth = depth + 1
            # logger.info("after substitution at depth %d, template is:\n%s" % (depth, template_string))
            if depth > max_depth:
                raise RuntimeError("template substitution recursion depth exceeded")

        return template_string

    # --------------------------------------------------------------------------
    def load_config_dict(self, filename, keyword=None):
        """
        Find configuration file and load it, optionally return keyword from within it.
        """

        # -------------------------------------------------------------------------
        # Name of config file comes on command line.
        if filename is not None:
            if "/" not in filename:
                # If no slash in filename, then file expected in the same folder as this module.
                script_path = os.path.dirname(__file__)
                filename = script_path + "/" + filename

        try:
            # Read the configuration json file.
            with open(filename, "r") as config_handle:
                config_dict = json.load(config_handle)
        except Exception as exception:
            raise RuntimeError(
                "unable to open the configuration file %s" % (filename)
            ) from exception

        if keyword is not None:
            config_dict = config_dict.get(keyword)

            if config_dict is None:
                raise RuntimeError(
                    "configuration file %s does not contain keyword %s"
                    % (filename, keyword)
                )

        return config_dict
