PYTHON  := python
MAIN    := ./src/main.py
SCRIPTS := ./tests
VFS     := ./tests

.PHONY: run run-vfs-minimal run-vfs-few run-vfs-many run-error clean

run:
	$(PYTHON) $(MAIN)

run-vfs-minimal:
	$(PYTHON) $(MAIN) --vfs $(VFS)/vfs_minimal.json --script $(SCRIPTS)/script_default.txt

run-vfs-few:
	$(PYTHON) $(MAIN) --vfs $(VFS)/vfs_few_files.json --script $(SCRIPTS)/script_default.txt

run-vfs-many:
	$(PYTHON) $(MAIN) --vfs $(VFS)/vfs_many_levels.json --script $(SCRIPTS)/script_many_levels.txt

run-error:
	$(PYTHON) $(MAIN) --vfs ./vfs/vfs_minimal.json

clean:
	rm -rf ../src/__pycache__ ./__pycache__