#!/usr/bin/env python3

import subprocess
import sys

def list_installed_packages():
    try:
        output = subprocess.check_output(
            ["rpm", "-qa", "--queryformat", "%{NAME} %{VERSION}-%{RELEASE}\n"],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print("Failed to query installed packages:", file=sys.stderr)
        print(exc.output, file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("rpm command not found. This script is for RPM-based systems like Red Hat.", file=sys.stderr)
        return 2

    packages = [line.strip() for line in output.splitlines() if line.strip()]
    for package in packages:
        print(package)

    return 0

if __name__ == "__main__":
    sys.exit(list_installed_packages())