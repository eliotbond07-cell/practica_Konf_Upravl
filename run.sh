#!/usr/bin/env bash
python3 ./src/main.py

python3 ./src/main.py --vfs ./tests/vfs_default.json

python3 ./src/main.py --script ./tests/script_default.txt

python3 ./src/main.py --vfs ./tests/vfs_default.json --script ./tests/script_default.txt

python3 ./src/main.py --script ./tests/script_error.txt