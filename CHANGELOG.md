# Changelog

## [0.1.2] - 2025-12-05

### Changed
- **Kernel controls** - Updated module availability controls based on CIS recommendations
- **Service controls** - Updated service status controls based on CIS recommendations
- **CLI interface** - Improved command-line interface with better usability

## [0.1.1] - 2025-12-03

### Added

- **Filesystem controls** - Implemented partitioning control
- **Kernel controls**
    - Implemented module availability control
    - Implemented module loadability control
- **Service controls** - Implemented service active status control

### Changed
- **Filesystem controls** - Improved permission control
- **Service controls** - Improved service enable status control
- **PoC templates** - Updated PoC templates with additional security controls

## [0.1.0] - 2025-11-28

### Added
**MVP release** - Linux security auditing tool based on CIS benchmarks

Features:

- **OS detection** - OS detection capabilities
- **Audit engine** - Local audit engine for security assessment
- **Security controls** - Jinja2-based controls with registry engine and structured results
- **Local executor** - Local execution framework used to run security controls
- **CLI interface** - Command-line interface built with Typer
- **JSON exporter** - Export audit results in a JSON format

### Dependencies
- distro >= 1.9.0
- Jinja2 >= 3.1.6
- pytest >= 9.0.1
- rich >= 14.2.0
- typer >= 0.20.0