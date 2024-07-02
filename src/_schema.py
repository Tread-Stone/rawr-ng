from pathlib import Path
from schema import Schema, Optional, SchemaError
from yaml import safe_load as yaml_load
from typing import Dict, Sequence

RawrNGSchema = Schema({
    "input": {
        "path": str,
        "type": str
    },
    Optional("enumeration", default=dict): {
        Optional("no_rdp", default=False): bool,
        Optional("no_vnc", default=False): bool,
        Optional("dns_dig", default=False): bool,
        Optional("get_options", default=False): bool,
        Optional("get_robots", default=False): bool,
        Optional("get_crossdomain", default=False): bool
    },
    Optional("requests", default=dict): {
        Optional("http_version", default="http1.1"): str,
        Optional("user_agent_preset", default="firefox"): str,
        Optional("proxy", default=None): Optional(str),
    },
    Optional("crawl", default=dict): {
        Optional("max_depth", default=3): int,
        Optional("max_num_pages", default=10): int,
        Optional("max_num_subdomains", default=100): int,
        Optional("timeout", default=180): int,
        Optional("mirror", default=False): bool,
        Optional("alternate_domains", default=list): list[str],
        Optional("blacklist", default=False): bool,
    },
    "output": {
        "path": str,
        "format": str,
        Optional("report_title", default="rawr-ng report"): str,
        Optional("report_logo_path", default=None): str,
        Optional("show_all", default=False): bool,
        Optional("show_default_passwords", default=False): bool,
    },
})


type YamlValue = str | int | float | bool | None | Sequence[YamlValue] | YamlDict
"""Recursive type definition for YAML values. Can be any primitive type, a list of YAML values (of any of these types, including another yaml dictionary), or a dictionary of YAML values (of any of these types)."""


type YamlDict = Dict[str, YamlValue]
"""Recursive type definition for YAML dictionaries. A dictionary of YAML values (of any of these types)."""


def read_config(config_path: Path | str) -> YamlDict:
    """Read and validate the configuration file.

    Args:
        config_path (Path | str): The path to the configuration file.

    Returns:
        dict: The validated configuration dictionary.
    """
    # Open the configuration file as text, so we can parse and validate it.
    with open(config_path) as file:
        try:
            # Load the file as from a yaml to a dictionary and validate its contents.
            return RawrNGSchema.validate(yaml_load(file))
        except SchemaError as e:
            # If the schema checker raises an error, re-raise it as a ValueError.
            raise ValueError("Invalid configuration file") from e

