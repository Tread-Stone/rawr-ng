from pathlib import Path
from schema import Schema, Optional, Or
from yaml import safe_load as yaml_load

ConfigSchema = Schema({
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


def read_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml_load(f)

if __name__ == "__main__":
    ConfigSchema.validate(read_config(Path("rawr_example_config.yaml")))

