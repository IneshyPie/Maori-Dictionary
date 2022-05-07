from pathlib import Path
for path in Path('.\static\images').iterdir():
    print(path.name)