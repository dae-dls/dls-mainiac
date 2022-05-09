import pytest
import time

import os
from subprocess import Popen
import psutil

# Function under test.
from dls_mainiac_lib.duplicate import interrupt_duplicate_commandlines

import logging

logger = logging.getLogger(__name__)


class Test_05_duplicate:

    # ----------------------------------------------------------------------------------------
    def test_05_duplicate(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """
        Test discovery and kill of duplicate commandline processes.
        """

        failure_message = None
        try:

            processes = []

            # Fire up three identical processes.
            for i in range(3):
                args = []

                args.append("python3")
                args.append("-m")
                args.append("tests.wilt")
                args.append(output_directory)

                # Run the process.
                pid = Popen(
                    args,
                    shell=False,
                    stdin=None,
                    stdout=None,
                    stderr=None,
                    close_fds=True,
                    preexec_fn=os.setsid,
                ).pid

                processes.append(psutil.Process(pid))

            # Give the processes a chance to become alive.
            time.sleep(0.5)

            # Kill all duplicates of the first.
            interrupt_duplicate_commandlines(this_process=processes[0])

            # Wait for all processes to die.
            gone, alive = psutil.wait_procs(processes, timeout=2.5)
            assert len(gone) == 3

            # First one dies of old age, the other two die of interrupt.
            assert processes[0].returncode == 1
            assert processes[1].returncode == 2
            assert processes[2].returncode == 2

        except Exception as exception:
            logger.exception("unexpected exception during the test", exc_info=exception)
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)
