# -*- coding: utf-8 -*-
# 存放"需要跨任务/跨循环记住"的状态。
属性列表 = ["火力", "鱼雷", "装甲", "对空"]
已耗尽属性 = set()
当前船可强化属性 = []
当前船名 = ""

# 累加器：{key: 累计值}，进程内持久，跨任务不丢
累加值 = {}


def 重置():
    """开始一次完整任务前调用，清空相关的记忆。

    """
    已耗尽属性.clear()
    当前船可强化属性.clear()
    global 当前船名
    当前船名 = ""
    累加值.clear()
    识别缓存.clear()


def 重置累加():
    """清空累加值。用于需要重新开始统计的场景。"""
    累加值.clear()


def 累加(key: str, value: float) -> float:
    """把 value 加到 key 上，返回累加后的值。"""
    累加值[key] = 累加值.get(key, 0) + value
    return 累加值[key]

# 识别结果缓存：{key: 文本}，供 dynamic_ocr 的 from_cache 读取
识别缓存 = {}


def 重置缓存():
    识别缓存.clear()


def 存识别缓存(key: str, value: str) -> None:
    识别缓存[key] = value


def 取识别缓存(key: str, default: str = "") -> str:
    return 识别缓存.get(key, default)