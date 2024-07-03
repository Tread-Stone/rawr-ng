from pathlib import Path
import re

def parse_nmap(nmap_file: Path):
    # Compile the regex pattern for numbers 1-9 at the start of the line
    pattern = re.compile(r"^\s*[1-9]")

    with open(nmap_file, "r") as file:
        for line in file:
            if pattern.match(line):
                print(line.strip())

if __name__ == "__main__":
    parse_nmap(Path("example.txt"))
