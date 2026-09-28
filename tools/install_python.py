#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下载 python-build-standalone 的独立 Python 到目标目录，并配置 pip。

用途：为发布包内嵌一个自带的 Python 运行时，供 Agent（自定义识别 / 自定义动作）
使用，从而让终端用户无需自行安装 Python 即可运行自动强化等功能。

用法:
    python install_python.py <目标目录>
示例:
    python install_python.py ./python-embed

注意：本脚本会下载当前运行平台对应的 Python，因此必须在目标平台的 runner 上执行
（例如为 Windows 包就要在 Windows runner 上跑）。
"""

import os
import sys
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path

# python-build-standalone 发布 tag 与 Python 版本（MaaFw 要求 >=3.9）
RELEASE_TAG = "20251209"
PYTHON_VERSION = "3.12.12"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


def get_download_url() -> str:
    system = platform.system()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64", "x64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64", "armv8", "armv8-a"):
        arch = "aarch64"
    else:
        sys.exit(f"不支持的架构: {machine}")

    if system == "Windows":
        triple = f"{arch}-pc-windows-msvc"
    elif system == "Darwin":
        triple = f"{arch}-apple-darwin"
    elif system == "Linux":
        triple = f"{arch}-unknown-linux-gnu"
    else:
        sys.exit(f"不支持的操作系统: {system}")

    base = (
        "https://github.com/astral-sh/python-build-standalone/releases/download/"
        f"{RELEASE_TAG}"
    )
    return (
        f"{base}/cpython-{PYTHON_VERSION}+{RELEASE_TAG}-{triple}"
        "-install_only_stripped.tar.gz"
    )


def find_python(dest: Path):
    candidates = [
        dest / "python.exe",
        dest / "bin" / "python3",
        dest / "bin" / "python",
        dest / "python",
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            if os.name != "nt":
                os.chmod(p, 0o755)
            return p
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python install_python.py <目标目录>")

    dest = Path(sys.argv[1]).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    url = get_download_url()
    archive = dest.parent / "python-embed-download.tar.gz"

    print(f"下载 Python: {url}")
    with urllib.request.urlopen(url) as resp, open(archive, "wb") as f:
        shutil.copyfileobj(resp, f)

    if not shutil.which("tar"):
        sys.exit("错误: 未找到 tar 命令")

    print(f"解压到: {dest}")
    # install_only 包顶层是一个 python/ 目录，去掉这一层直接铺到目标目录
    subprocess.run(
        ["tar", "-xzf", str(archive), "-C", str(dest), "--strip-components=1"],
        check=True,
    )
    try:
        archive.unlink()
    except OSError:
        pass

    py = find_python(dest)
    if not py:
        sys.exit("错误: 解压后未找到 Python 可执行文件")

    # 确保 pip 可用（standalone 一般自带 pip，这里再兜底执行一次 get-pip）
    get_pip = dest / "get-pip.py"
    print("配置 pip ...")
    with urllib.request.urlopen(GET_PIP_URL) as resp, open(get_pip, "wb") as f:
        shutil.copyfileobj(resp, f)
    subprocess.run([str(py), str(get_pip)], check=True)
    try:
        get_pip.unlink()
    except OSError:
        pass

    print(f"完成，Python 位于: {py}")


if __name__ == "__main__":
    main()
