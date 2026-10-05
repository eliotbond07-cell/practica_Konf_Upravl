#!/usr/bin/env bash
python3 ./src/main.py

python3 ./src/main.py --vfs ./tests/vfs_minimal.json --script ./tests/script_default.txt

python3 ./src/main.py --script ./tests/vfs_few_files.json --script ./tests/script_default.txt

python3 ./src/main.py --vfs ./tests/vfs_many_levels.json --script ./tests/script_many_levels.txt

python3 ./src/main.py --vfs ./vfs/vfs_minimal.json