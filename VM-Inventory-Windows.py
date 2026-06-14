#!/usr/bin/env python3
"""List installed software packages on a Windows laptop."""

import sys
import platform

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None


def _read_uninstall_key(root, path):
    results = []

    try:
        with winreg.OpenKey(root, path) as key:
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        package = {
                            "name": _get_reg_value(subkey, "DisplayName"),
                            "version": _get_reg_value(subkey, "DisplayVersion"),
                            "publisher": _get_reg_value(subkey, "Publisher"),
                            "install_location": _get_reg_value(subkey, "InstallLocation"),
                            "uninstall_string": _get_reg_value(subkey, "UninstallString"),
                        }
                        if package["name"]:
                            results.append(package)
                except OSError:
                    continue
    except FileNotFoundError:
        return []

    return results


def _get_reg_value(key, value_name):
    try:
        value, _ = winreg.QueryValueEx(key, value_name)
        return str(value).strip()
    except OSError:
        return ""


def list_installed_software():
    if platform.system() != "Windows":
        print("This script only runs on Windows.", file=sys.stderr)
        return 1

    if winreg is None:
        print("The winreg module is unavailable in this Python environment.", file=sys.stderr)
        return 2

    uninstall_roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]

    packages = []
    seen = set()

    for root, path in uninstall_roots:
        for package in _read_uninstall_key(root, path):
            key = (package["name"], package["version"])
            if key not in seen:
                seen.add(key)
                packages.append(package)

    packages.sort(key=lambda item: (item["name"].lower() if item["name"] else "", item["version"]))

    if not packages:
        print("No installed software packages were found.")
        return 0

    print("Name,Version,Publisher,InstallLocation,UninstallString")
    for package in packages:
        print(",".join(
            _escape_csv(value)
            for value in (
                package["name"],
                package["version"],
                package["publisher"],
                package["install_location"],
                package["uninstall_string"],
            )
        ))

    return 0


def _escape_csv(value):
    if value is None:
        return ""
    escaped = str(value).replace('"', '""')
    if "," in escaped or '"' in escaped or "\n" in escaped or "\r" in escaped:
        return f'"{escaped}"'
    return escaped


if __name__ == "__main__":
    sys.exit(list_installed_software())
