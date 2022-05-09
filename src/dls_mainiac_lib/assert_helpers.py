import pytest
import contextlib
import io
import sys


import logging

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


# ----------------------------------------------------------------------------------------
def assert_parse_system_exit(
    case, app, arglist, exit_code=None, stdout_contains=None, stderr_contains=None
):
    """
    Make sure the expected parse exit is handled.
    """

    # Capture the printing of the help and syntax messages.
    with captured_output() as (captured_stdout, captured_stderr):
        # with pytest.raises(SystemExit) as exc_info:
        exception = None
        try:
            app.parse_args(arglist)
        except SystemExit as e:
            exception = e

        if exception is None:
            assert False, "%s did not raise SystemExit" % (case)

        # TODO: Figure out how to assert exit code from SystemExit exception.
        # assert exc_info.value.code == exit_code

        captured_stdout.seek(0)
        captured_stdout = captured_stdout.read()

        captured_stderr.seek(0)
        captured_stderr = captured_stderr.read()

        if stdout_contains is not None:
            if stdout_contains not in captured_stdout:
                logger.info(
                    "failed %s %s\nstdout expected to contain: %s\n but is actually:\n%s"
                    % (case, str(arglist), stdout_contains, captured_stdout)
                )
                assert False, case
        else:
            if captured_stdout != "":
                logger.info("stdout: %s" % (captured_stdout))

        if stderr_contains is not None:
            if stderr_contains not in captured_stderr:
                logger.info(
                    "failed %s %s\nstderr expected to contain: %s\n but is actually:\n%s"
                    % (case, str(arglist), stderr_contains, captured_stderr)
                )
                assert False, case
        else:
            if captured_stderr != "":
                logger.info("stderr: %s" % (captured_stderr))


# ----------------------------------------------------------------------------------------
def assert_parse_success(case, app, arglist):

    # Capture the printing of the help and syntax messages.
    with captured_output() as (captured_stdout, captured_stderr):
        try:
            app.parse_args(arglist)
        except Exception as exception:
            captured_stderr.seek(0)
            captured_stderr = captured_stderr.read()
            logger.info(
                "failed %s %s\nstderr:\n%s" % (case, str(arglist), captured_stderr)
            )
            assert False, case
