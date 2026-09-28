from pathlib import Path

import shutil
import sys
import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from configure import configure_ocr_model

# 修正：指向仓库根目录
working_dir = Path(__file__).parent.parent.resolve()
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
    interface["mirrorchyan_rid"] = "MaaJR-MXU"

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(working_dir / "README.md", install_path)
    shutil.copy2(working_dir / "LICENSE", install_path)


def install_agent():
    """复制 agent 代码，并在存在内嵌 Python（python-embed）时一并打包，
    同时把 interface.json 的 agent 段指向内嵌 Python，实现开箱即用。
    注意：MXU 的 maafw 二进制在 install-mxu/maafw，而 agent 与 python 放在
    install-mxu 根目录（interface.json 同级），child_exec 相对 interface.json 解析。"""
    shutil.copytree(
        working_dir / "agent",
        install_path / "agent",
        dirs_exist_ok=True,
    )

    py_src = working_dir / "python-embed"
    if not py_src.exists():
        print("未找到 python-embed，跳过内嵌 Python 打包与 agent 段改写。")
        return

    shutil.copytree(py_src, install_path / "python", dirs_exist_ok=True)

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    agent = interface.get("agent") or {}
    if os_name == "win":
        agent["child_exec"] = "./python/python.exe"
    else:  # macos / linux
        agent["child_exec"] = "./python/bin/python3"
    agent["child_args"] = ["-u", "./agent/main.py"]
    interface["agent"] = agent

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    install_agent()
    print(f"Install MXU to {install_path} successfully.")
