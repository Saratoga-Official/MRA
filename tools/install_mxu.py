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
install_path = working_dir / "install-mxu"

# 接受三个参数：version, os, arch（后两个参数保留以备将来使用，MXU 版本暂时不依赖平台）
if len(sys.argv) < 4:
    print("Usage: python install_mxu.py <version> <os> <arch>")
    print("Example: python install_mxu.py v1.2.3 win x86_64")
    sys.exit(1)

version = sys.argv[1]
os_name = sys.argv[2]   # 当前未使用
arch = sys.argv[3]      # 当前未使用


def install_deps():
    """安装 MaaFramework 依赖到 maafw 目录（MXU 要求的目录结构）

    MXU 要求将 MaaFramework 的 bin 文件夹内容解压到 maafw 文件夹中。
    参考: https://github.com/MistEO/MXU#依赖文件
    """

    # MaaFramework 运行库 → maafw/
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

    # 定制版本、标题和 mirrorchyan 资源 ID
    interface["version"] = version
    interface["title"] = f"MRA {version}"
    # interface["mirrorchyan_rid"] = "MRA-MXU"

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    """复制基本文档（仅 README.md 和 LICENSE，与脚本2一致）"""
    shutil.copy2(working_dir / "README.md", install_path)
    shutil.copy2(working_dir / "LICENSE", install_path)


def install_manifest_cache():
    """生成初始 manifest 缓存，加速用户首次启动"""
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

    print(f"Install MXU to {install_path} successfully.")