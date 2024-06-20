from yaml import safe_load as yaml_load
from pathlib import Path
from typing import TypedDict, Sequence, Dict
from enum import Enum, Flag, auto as enum_auto


class ScannerType(Enum):
    nmap = "nmap"
    rustscan = "rustscan"


class ScannerConfig(TypedDict):
    scanner_type: ScannerType
    scanner_path: str


class EnumerationConfig(Flag):
    no_rdp = enum_auto() # 1
    no_vnc = enum_auto() # 2
    dns_dig = enum_auto() # 4
    get_options = enum_auto() # 8
    get_robots = enum_auto() # 16
    get_crossdomain = enum_auto() # 32
    no_captures = no_rdp | no_vnc # 1 + 2 = 3


class HttpVersion(Enum):
    http1 = "http1.0"
    http2 = "http1.1"
    http3 = "http2.0"


type HttpProxy = str | None


class UserAgentPreset(Enum):
    firefox = "firefox"


class RequestConfig(TypedDict):
    http_version: HttpVersion
    user_agent: UserAgentPreset
    proxy: HttpProxy


class CrawlConfig(TypedDict):
    max_num_subdomains: Optional[int]
    max_num_pages: Optional[int]
    max_depth: Optional[int]
    timeout: int
    mirror: bool
    alternate_domains: Sequence[str]
    blacklist: bool



class OutputOptions(Flag):
    silent = enum_auto()
    verbose = enum_auto()
    include_default_passwords = enum_auto()

class OutputConfig(TypedDict):
    output_options: OutputOptions
    output_file: str
    output_dir: str


type YamlValue = str | int | float | bool | None | Sequence[YamlValue] | YamlDict


type YamlDict = Dict[str, YamlValue]




def read_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml_load(f)

if __name__ == "__main__":
    print(read_config(Path("rawr_example_config.yaml")))
