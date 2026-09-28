"""把 Android 出包需要、但不在 assets/ 里的文件铺进 assets/。

MaaFwApp 配方（Android/profile.yaml）的 include 只能匹配 assets 目录里的文件，
而 agent/、LICENSE、logo.ico 在仓库根，所以出包前要先铺一次。产物已加进 .gitignore。

用法：
    python tools/stage_android.py                 # 本地出包
    python tools/stage_android.py --version v1.2.3  # CI：顺带把 interface.json 的版本号换成本次 tag
"""

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

root = Path(__file__).resolve().parents[1]
assets_dir = root / "assets"


def stage_agent():
    target = assets_dir / "agent"
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(
        root / "agent",
        target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def stage_license():
    shutil.copy2(root / "LICENSE", assets_dir / "LICENSE")


def stage_icon():
    # Android 不解码 ico；launcher 图标与 PI 图标都用转出的 png
    with Image.open(root / "logo.ico") as ico:
        ico.save(assets_dir / "logo.png")


def stamp_version(version: str):
    # 与 tools/install.py 的 install_resource 一致
    path = assets_dir / "interface.json"
    with open(path, encoding="utf-8") as f:
        interface = json.load(f)
    interface["version"] = version
    interface["title"] = f"MRA {version} | 舰R小助手"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage MRA files for MaaFwApp Android packaging")
    parser.add_argument("--version", help="写进 interface.json 的版本号（CI 用）")
    args = parser.parse_args()

    stage_agent()
    stage_license()
    stage_icon()
    if args.version:
        stamp_version(args.version)
    print("Android assets staged.")
