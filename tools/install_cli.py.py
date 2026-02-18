from pathlib import Path

import shutil
import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from configure import configure_ocr_model
from generate_manifest_cache import generate_manifest_cache

working_dir = Path(__file__).parent.parent.parent
install_path = working_dir / "install-cli"

# 接受三个参数：version, os, arch
if len(sys.argv) < 4:
    print("Usage: python install_cli.py <version> <os> <arch>")
    print("Example: python install_cli.py v1.2.3 win x86_64")
    sys.exit(1)

version = sys.argv[1]
os_name = sys.argv[2]   # 保留以备将来使用，目前未用
arch = sys.argv[3]      # 保留以备将来使用，目前未用


def install_deps():
    """复制 MaaFramework 依赖（CLI 版本直接放在根目录），不包含 Agent 相关文件"""
    shutil.copytree(
        working_dir / "deps" / "bin",
        install_path,
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaWin32ControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
        ),
        dirs_exist_ok=True,
    )
    # 注意：不再复制 MaaAgentBinary


def install_resource():
    """复制资源文件并定制 interface.json"""
    configure_ocr_model()

    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )
    shutil.copy2(
        working_dir / "assets" / "interface_cli.json",
        install_path / "interface.json",
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    # 定制版本和标题
    interface["version"] = version
    interface["title"] = f"MRA {version}"

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    """复制基本文档（仅 README.md 和 LICENSE，与脚本2一致）"""
    shutil.copy2(working_dir / "README.md", install_path)
    shutil.copy2(working_dir / "LICENSE", install_path)


def install_manifest_cache():
    """生成 manifest 缓存，加速用户首次启动"""
    config_dir = install_path / "config"
    success = generate_manifest_cache(config_dir)
    if success:
        print("Manifest cache generated successfully.")
    else:
        print(
            "Warning: Manifest cache generation failed, users will do full check on first run."
        )


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    install_manifest_cache()

    print(f"Install to {install_path} successfully.")