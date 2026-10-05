@echo off
python .\src\main.py

python .\src\main.py --vfs .\tests\vfs_minimal.json --script .\tests\script_default.txt

python .\src\main.py --vfs .\tests\vfs_few_files.json --script .\tests\script_default.txt

python .\src\main.py --vfs .\tests\vfs_many_levels.json --script .\tests\script_many_levels.txt

python .\src\main.py --vfs .\vfs\vfs_minimal.json