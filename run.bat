@echo off
python .\src\main.py

python .\src\main.py --vfs .\tests\vfs_default.json

python .\src\main.py --script .\tests\script_default.txt

python .\src\main.py --vfs .\tests\vfs_default.json --script .\tests\script_default.txt

python .\src\main.py --script .\tests\script_error.txt