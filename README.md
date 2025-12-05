<div align="center">

# **Horus**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-GPLv3-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.2-orange.svg)](CHANGELOG.md)

**Linux security auditing tool based on CIS benchmarks**

</div>

## Requirements

- **Python**: 3.11 or higher
- **OS**: Linux distributions

## Quick start

### Installation

```
# Clone the repository
git clone https://github.com/samydflh/Horus.git
cd Horus

# Initialize a virtual environment
python -m venv .env
source .env/bin/activate

# Install dependencies
pip install -e .

# Run Horus
horus audit
```

### Usage

Run a local security audit on your host:

```bash
horus audit
```

Generate a JSON report:

```bash
horus audit --json report.json
```

## Features

- **OS detection** - OS detection capabilities
- **Audit engine** - Local audit engine for security assessment
- **Security controls** - Jinja2-based controls with registry engine and structured results
- **Local executor** - Local execution framework used to run security controls
- **CLI interface** - Command-line interface built with Typer
- **JSON exporter** - Export audit results in a JSON format

## Dependencies

- `distro >= 1.9.0`
- `Jinja2 >= 3.1.6`
- `rich >= 14.2.0`
- `typer >= 0.20.0`

## License

This project is licensed under [GPLv3 License](LICENSE).

## Links

- [Changelog](CHANGELOG.md)
- [CIS benchmarks](https://www.cisecurity.org/cis-benchmarks)