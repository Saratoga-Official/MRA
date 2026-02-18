from pathlib import Path

import shutil
import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from configure import configure_ocr_model

working_dir = Path(__file__).parent.parent.parent
install_path = working_dir / "install-mxu"

if len(sys.argv) < 4:
    print("Usage: python install_mxu.py <version> <os> <arch>")
    print("Example: python install_mxu.py v1.2.3 win x86_64")
    sys.exit(1)

version = sys.argv[1]
os_name = sys.argv[2]
arch = sys.argv[3]


def install_deps():
    shutil.copytree(
        working_dir / "deps" / "bin",
        install_path / "maafw",
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaWin32ControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
            "*.node",
            "*MaaPiCli*",
        ),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        working_dir / "deps" / "share" / "MaaAgentBinary",
        install_path / "maafw" / "MaaAgentBinary",
        dirs_exist_ok=True,
    )


def install_resource():
    configure_ocr_model()

    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )
    shutil.copy2(
        working_dir / "assets" / "interface.json",
        install_path,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    interface["version"] = version
    interface["title"] = f"MRA {version} | 舰R小助手"
    # interface["mirrorchyan_rid"] = "MRA-MXU"

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(working_dir / "README.md", install_path)
    shutil.copy2(working_dir / "LICENSE", install_path)


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    print(f"Install MXU to {install_path} successfully.")