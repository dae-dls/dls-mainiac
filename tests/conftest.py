import os
import shutil
import json

import pytest

# Version of the package.
from dls_mainiac_lib.version import meta as version_meta

# Formatting of testing log messages.
from dls_logform.dls_logform import DlsLogform

import logging

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def constants(request):

    constants = {}

    constants["mainiac_database_endpoint"] = "%s/mainiac.sqlite"
    constants["mainiac_port"] = 15006
    constants["mainiac_server_endpoint"] = "tcp://*:%d" % (constants["mainiac_port"])
    constants["mainiac_client_endpoint"] = "tcp://localhost:%d" % (
        constants["mainiac_port"]
    )

    constants["protocolj_port"] = 15007
    constants["protocolj_client_endpoint"] = "http://localhost:%d" % (
        constants["protocolj_port"]
    )

    yield constants


# --------------------------------------------------------------------------------
@pytest.fixture()
def logging_setup():

    formatter = DlsLogform(type="long")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

    # Log level for all modules.
    logging.getLogger().setLevel("DEBUG")

    # Cover the version.
    logger.info("\n%s", (json.dumps(version_meta(), indent=4)))

    yield None


# --------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def output_directory(request):

    # Tmp directory which we can write into.
    output_directory = "/tmp/%s/%s/%s" % (
        "/".join(__file__.split("/")[-3:-1]),
        request.cls.__name__,
        request.function.__name__,
    )

    # Tmp directory which we can write into.
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory, ignore_errors=False, onerror=None)
    os.makedirs(output_directory)

    # logger.debug("output_directory is %s" % (output_directory))

    yield output_directory
