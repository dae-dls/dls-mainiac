# This is needed so local copy of dependencies supercede the installed ones.
BASIC_PATH=src:../dls-signals/src:../dls-logform/src
PYTHONPATH=$(BASIC_PATH)

# ------------------------------------------------------------------
# Tests individually.

test-01-simple:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest -sv -ra --tb=line tests/test_01_simple.py

test-02-subcommand:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest -sv -ra --tb=line tests/test_02_subcommand.py
	
test-03-default_subcommand:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest -sv -ra --tb=line tests/test_03_default_subcommand.py
	
test-04-rotating:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest -sv -ra --tb=line tests/test_04_rotating.py
	
test-05-duplicate:
	PYTHONPATH=$(PYTHONPATH) python3 -m pytest -sv -ra --tb=line tests/test_05_duplicate.py
	
# ------------------------------------------------------------------
# GitLab CI.

gitlab_ci_test: 
	python3 -m pytest -sv -ra --tb=line --cov=dls_mainiac_lib tests

test-ci:
	PYTHONPATH=$(PYTHONPATH) make gitlab_ci_test

pytest:
	PYTHONPATH=$(PYTHONPATH) pytest
	
gitrun-unittest:
	gitlab-runner exec docker unittest

# ------------------------------------------------------------------
# Utility.

tree:
	tree -I "__*" dls_mainiac_lib

	tree -I "__*" tests

.PHONY: list
list:
	@awk "/^[^\t:]+[:]/" Makefile | grep -v ".PHONY"

clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '__pycache__' -exec rm -rf {} \;

show-version:
	PYTHONPATH=$(PYTHONPATH) python3 -m dls_mainiac_lib.version --json
	PYTHONPATH=$(PYTHONPATH) python3 -m dls_mainiac_lib.version

# ------------------------------------------------------------------
# Version bumping.  Configured in setup.cfg. 
# Thanks: https://pypi.org/project/bump2version/
bump-patch:
	bump2version --list patch

bump-minor:
	bump2version --list minor

bump-major:
	bump2version --list major
	
bump-dryrun:
	bump2version --dry-run patch
	