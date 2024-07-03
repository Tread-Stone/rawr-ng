from pathlib import Path

def parse_nmap(nmap_file: Path):
    file = open(nmap_file, "r")
    body = file.read().split("\n")
    print(body)
    line = file.readline().strip()
    print(line)

if __name__ == "__main__":
    parse_nmap(Path("nmap_file.txt"))
