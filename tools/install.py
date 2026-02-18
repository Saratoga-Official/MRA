from pathlib import Path

import shutil
import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from configure import configure_ocr_model

working_dir = Path(__file__).parent.parent.resolve()
install_path = working_dir / "install"

if len(sys.argv) < 4:
    print("Usage: python install.py <version> <os> <arch>")
    print("Example: python install.py v1.2.3 win x86_64")
    sys.exit(1)

version = sys.argv[1]
os_name = sys.argv[2]
arch = sys.argv[3]


def get_dotnet_platform_tag():
    """根据 os 和 arch 返回 dotnet 平台标签"""
    if os_name == "win" and arch == "x86_64":
        return "win-x64"
    elif os_name == "win" and arch == "aarch64":
        return "win-arm64"
    elif os_name == "macos" and arch == "x86_64":
        return "osx-x64"
    elif os_name == "macos" and arch == "aarch64":
        return "osx-arm64"
    elif os_name == "linux" and arch == "x86_64":
        return "linux-x64"
    elif os_name == "linux" and arch == "aarch64":
        return "linux-arm64"
    else:
        print("Unsupported OS or architecture.")
        sys.exit(1)


def install_deps():
    if not (working_dir / "deps" / "bin").exists():
        print('请先下载 MaaFramework 到 "deps" 目录')
        sys.exit(1)

    if os_name == "android":
        shutil.copytree(
            working_dir / "deps" / "bin",
            install_path,
            dirs_exist_ok=True,
        )
        shutil.copytree(
            working_dir / "deps" / "share" / "MaaAgentBinary",
            install_path / "MaaAgentBinary",
            dirs_exist_ok=True,
        )
    else:
        platform_tag = get_dotnet_platform_tag()
        shutil.copytree(
            working_dir / "deps" / "bin",
            install_path / "runtimes" / platform_tag / "native",
            ignore=shutil.ignore_patterns(
                "*MaaDbgControlUnit*",
                "*MaaThriftControlUnit*",
                "*MaaRpc*",
                "*MaaHttp*",
                "plugins",
                "*.node",
                "*MaaPiCli*",
            ),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            working_dir / "deps" / "share" / "MaaAgentBinary",
            install_path / "libs" / "MaaAgentBinary",
            dirs_exist_ok=True,
        )
        shutil.copytree(
            working_dir / "deps" / "bin" / "plugins",
            install_path / "plugins" / platform_tag,
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

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(working_dir / "README.md", install_path)
    shutil.copy2(working_dir / "LICENSE", install_path)


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    print(f"Install to {install_path} successfully.")