"""Device fingerprinting for hardware-based licensing."""

import hashlib
import platform
import subprocess
import sys
import uuid
from dataclasses import dataclass
from typing import Optional

# Hide console window on Windows when running subprocess
_SUBPROCESS_KWARGS = {}
if sys.platform == 'win32':
    _SUBPROCESS_KWARGS['creationflags'] = getattr(
        subprocess, 'CREATE_NO_WINDOW', 0x08000000
    )


@dataclass
class DeviceInfo:
    """Device hardware information."""

    cpu_id: str
    disk_serial: str
    mac_address: str
    hostname: str
    os_info: str


def _get_windows_cpu_id() -> str:
    """Get CPU ID on Windows using PowerShell (primary) or wmic (fallback)."""
    # Try PowerShell first (works on Windows 10/11)
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Processor).ProcessorId"],
            capture_output=True, text=True, timeout=10,
            **_SUBPROCESS_KWARGS,
        )
        val = result.stdout.strip()
        if val:
            return val
    except Exception:
        pass
    # Fallback to wmic (older Windows)
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "ProcessorId"],
            capture_output=True, text=True, timeout=5,
            **_SUBPROCESS_KWARGS,
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            return lines[1].strip()
    except Exception:
        pass
    return ""


def _get_windows_disk_serial() -> str:
    """Get disk serial number on Windows using PowerShell (primary) or wmic (fallback)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_DiskDrive | Select-Object -First 1).SerialNumber"],
            capture_output=True, text=True, timeout=10,
            **_SUBPROCESS_KWARGS,
        )
        val = result.stdout.strip()
        if val:
            return val
    except Exception:
        pass
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            capture_output=True, text=True, timeout=5,
            **_SUBPROCESS_KWARGS,
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            return lines[1].strip()
    except Exception:
        pass
    return ""


def _get_mac_cpu_id() -> str:
    """Get CPU ID on macOS."""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        pass
    return ""


def _get_mac_disk_serial() -> str:
    """Get disk serial on macOS."""
    try:
        result = subprocess.run(
            ["system_profiler", "SPSerialATADataType"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Parse output for serial number
        for line in result.stdout.split("\n"):
            if "Serial Number:" in line:
                return line.split(":")[-1].strip()
    except Exception:
        pass
    return ""


def _get_linux_cpu_id() -> str:
    """Get CPU ID on Linux."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[-1].strip()
    except Exception:
        pass
    return ""


def _get_linux_disk_serial() -> str:
    """Get disk serial on Linux."""
    try:
        result = subprocess.run(
            ["lsblk", "-o", "SERIAL", "-d", "-n"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.strip().split("\n")
        if lines:
            return lines[0].strip()
    except Exception:
        pass
    return ""


def get_device_info() -> DeviceInfo:
    """Collect device hardware information.

    Returns:
        DeviceInfo object with hardware identifiers
    """
    system = platform.system()

    # Get CPU ID based on OS
    if system == "Windows":
        cpu_id = _get_windows_cpu_id()
        disk_serial = _get_windows_disk_serial()
    elif system == "Darwin":  # macOS
        cpu_id = _get_mac_cpu_id()
        disk_serial = _get_mac_disk_serial()
    elif system == "Linux":
        cpu_id = _get_linux_cpu_id()
        disk_serial = _get_linux_disk_serial()
    else:
        cpu_id = ""
        disk_serial = ""

    # Get MAC address
    mac = ":".join(
        ["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]
    )

    # Get hostname
    hostname = platform.node()

    # Get OS info
    os_info = f"{platform.system()} {platform.release()}"

    return DeviceInfo(
        cpu_id=cpu_id or "UNKNOWN_CPU",
        disk_serial=disk_serial or "UNKNOWN_DISK",
        mac_address=mac,
        hostname=hostname,
        os_info=os_info,
    )


def generate_device_fingerprint(device_info: Optional[DeviceInfo] = None) -> str:
    """Generate a unique device fingerprint hash.

    Args:
        device_info: Optional DeviceInfo object. If None, will collect automatically.

    Returns:
        SHA256 hash of device identifiers
    """
    if device_info is None:
        device_info = get_device_info()

    # Concatenate identifiers
    fingerprint_string = (
        f"{device_info.cpu_id}|"
        f"{device_info.disk_serial}|"
        f"{device_info.mac_address}|"
        f"{device_info.hostname}"
    )

    # Generate SHA256 hash
    fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()

    return fingerprint_hash


def verify_device_fingerprint(expected_fingerprint: str) -> bool:
    """Verify current device matches expected fingerprint.

    Args:
        expected_fingerprint: Expected device fingerprint hash

    Returns:
        True if fingerprints match
    """
    current_fingerprint = generate_device_fingerprint()
    return current_fingerprint == expected_fingerprint
