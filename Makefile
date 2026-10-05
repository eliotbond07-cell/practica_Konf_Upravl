PYTHON  := python
MAIN    := ./src/main.py
SCRIPTS := ./tests
VFS     := ./tests/vfs

.PHONY: run run-vfs run-script run-full run-error clean

run:
	$(PYTHON) $(MAIN)

run-vfs:
	$(PYTHON) $(MAIN) --vfs $(VFS)/vfs_default.json

run-script:
	$(PYTHON) $(MAIN) --script $(SCRIPTS)/script_default.txt

run-full:
	$(PYTHON) $(MAIN) --vfs $(VFS)/vfs_default.json --script $(SCRIPTS)/script_default.txt

run-error:
	$(PYTHON) $(MAIN) --script $(SCRIPTS)/script_error.txt

clean:
	rm -rf ../src/__pycache__ ./__pycache__