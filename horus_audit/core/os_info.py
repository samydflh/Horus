from dataclasses import dataclass
import platform

import distro

from horus_audit.config import config


logger = config.get_logger(__name__)


@dataclass
class OSInfo:
    distro_id: str
    name: str
    version: str
    major_version: str
    family: str
    kernel_version: str
    architecture: str
    hostname: str


def detect_os() -> OSInfo:
    """
    Detect the running Linux distribution with comprehensive information.

    Returns:
        OSInfo: OS information.
    """

    # Distribution information
    distro_id = distro.id().lower().strip()
    name = distro.name().strip()
    version = distro.version(pretty=True, best=True).strip()
    major_version = distro.major_version() or version.split(".")[0] if version else "unknown"

    # Distribution family
    family = None
    like = distro.like() or ""

    if not like:
        family = distro_id
    else:
        family = like.split()[0]

    # Kernel and system information
    uname = platform.uname()
    kernel_version = uname.release
    architecture = uname.machine
    hostname = uname.node

    logger.info(f"Detected OS: distro_id={distro_id}, name={name}, version={version}, family={family}")
    logger.info(f"System: kernel={kernel_version}, arch={architecture}, hostname={hostname}")

    return OSInfo(
        distro_id=distro_id,
        name=name,
        version=version,
        major_version=major_version,
        family=family,
        kernel_version=kernel_version,
        architecture=architecture,
        hostname=hostname
    )
