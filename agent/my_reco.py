# -*- coding: utf-8 -*-
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
import enhance_state as st
from logger import logger
import json
import re
def 记录识别(名称: str, detail) -> None:
    """把自定义识别结果打进文件日志（debug 级，不刷 UI），方便排查。"""
    logger.debug(f"[识别] {名称}: {detail}")
船位表 = [
    {
        "点击框": [59, 347, 124, 27],
        "格子": {
            "火力": [70, 282, 23, 16],
            "鱼雷": [100, 282, 23, 16],
            "装甲": [130, 282, 23, 16],
            "对空": [160, 282, 23, 16],
        },
    },
    {
        "点击框": [200, 347, 124, 27],
        "格子": {
            "火力": [211, 282, 23, 16],
            "鱼雷": [241, 282, 23, 16],
            "装甲": [271, 282, 23, 16],
            "对空": [301, 282, 23, 16],
        },
    },
    {
        "点击框": [341, 347, 124, 27],
        "格子": {
            "火力": [351, 282, 23, 16],
            "鱼雷": [381, 282, 23, 16],
            "装甲": [411, 282, 23, 16],
            "对空": [441, 282, 23, 16],
        },
    },
    {
        "点击框": [482, 347, 124, 27],
        "格子": {
            "火力": [492, 282, 23, 16],
            "鱼雷": [522, 282, 23, 16],
            "装甲": [552, 282, 23, 16],
            "对空": [582, 282, 23, 16],
        },
    },
    {
        "点击框": [622, 347, 124, 27],
        "格子": {
            "火力": [633, 282, 23, 16],
            "鱼雷": [663, 282, 23, 16],
            "装甲": [693, 282, 23, 16],
            "对空": [723, 282, 23, 16],
        },
    },
]
def 读一艘船(context: Context, image, 格子表: dict) -> list:
    """读一艘船的四个格子，返回它"可强化"（读到 + 或数字）的属性列表。
    纯函数，不写任何全局状态，供 enhance / upgrade 两个识别共用，互不影响。
    """
    可强化, _ = 读一艘船详情(context, image, 格子表)
    return 可强化
def 读一艘船详情(context: Context, image, 格子表: dict):
    """读一艘船四个格子，返回 (可强化属性列表, 每格详情dict)。
    详情格式：{属性名: "读到的原始文字" 或 "<未命中>"}，用于排查识别问题。
    """
    可强化 = []
    详情 = {}
    for 属性名, roi in 格子表.items():
        reco = context.run_recognition(
            "读强化格子",
            image,
            pipeline_override={"读强化格子": {"roi": roi}},
        )
        if reco is None or not reco.hit:
            详情[属性名] = "<未命中>"
            continue
        文字 = str(reco.best_result.text)
        详情[属性名] = 文字
        有加号 = "+" in 文字
        有数字 = any(c.isdigit() for c in 文字)
        if 有加号 or 有数字:
            可强化.append(属性名)
    return 可强化, 详情
def 读船名(context: Context, image, 点击框: list) -> str:
    """复用"读强化格子"OCR 节点，读点击框位置的船名。"""
    名字reco = context.run_recognition(
        "读强化格子",
        image,
        pipeline_override={"读强化格子": {"roi": 点击框}},
    )
    if 名字reco is not None and 名字reco.hit:
        return str(名字reco.best_result.text)
    return "未知舰船"
# ========== 识别1：在选船界面挑一艘该强化的船 ==========
@AgentServer.custom_recognition("select_ship_to_enhance")
class SelectShipToEnhance(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        for i, 船 in enumerate(船位表):
            可强化属性, 详情 = 读一艘船详情(context, argv.image, 船["格子"])
            记录识别("select_ship_to_enhance", f"船位{i + 1} 可强化={可强化属性 or '无'} 格子={详情}")
            有效属性 = [a for a in 可强化属性 if a not in st.已耗尽属性]
            if 有效属性:
                st.当前船可强化属性 = 可强化属性
                st.当前船名 = 读船名(context, argv.image, 船["点击框"])
                detail = {"船名": st.当前船名, "可强化": 可强化属性, "有效": 有效属性}
                记录识别("select_ship_to_enhance", f"选中 {detail}")
                return CustomRecognition.AnalyzeResult(
                    box=船["点击框"],
                    detail=detail,
                )
        记录识别("select_ship_to_enhance", "本屏无可强化的船")
        return CustomRecognition.AnalyzeResult(
            box=None,
            detail={"结论": "本屏无可强化的船"},
        )
# ========== 识别2：读素材界面右上角四个属性值 ==========
@AgentServer.custom_recognition("read_material_values")
class ReadMaterialValues(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        数值框 = {
            "火力": [1172, 106, 77, 31],
            "鱼雷": [1172, 142, 77, 31],
            "装甲": [1172, 178, 77, 31],
            "对空": [1172, 214, 77, 31],
        }
        数值 = {}
        for 属性名, roi in 数值框.items():
            reco = context.run_recognition(
                "读素材数值",
                argv.image,
                pipeline_override={"读素材数值": {"roi": roi}},
            )
            if reco is None or not reco.hit:
                数值[属性名] = 0
                continue
            try:
                数值[属性名] = int(str(reco.best_result.text).strip())
            except ValueError:
                数值[属性名] = 0
        记录识别("read_material_values", 数值)
        return CustomRecognition.AnalyzeResult(
            box=[0, 0, 1, 1],
            detail=数值,
        )
# ========== 识别3：读强化确认界面右侧四行的 MAX 状态 ==========
@AgentServer.custom_recognition("read_enhance_result")
class ReadEnhanceResult(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        行框 = {
            "火力": [1204, 119, 53, 30],
            "鱼雷": [1204, 205, 53, 30],
            "装甲": [1204, 291, 53, 30],
            "对空": [1204, 377, 53, 30],
        }
        结果 = {}
        for 属性名, roi in 行框.items():
            reco = context.run_recognition(
                "读强化结果",
                argv.image,
                pipeline_override={"读强化结果": {"roi": roi}},
            )
            if reco is None or not reco.hit:
                结果[属性名] = "不可强化"
            elif "MAX" in str(reco.best_result.text).upper():
                结果[属性名] = "MAX"
            else:
                结果[属性名] = "可强化"
        记录识别("read_enhance_result", 结果)
        return CustomRecognition.AnalyzeResult(
            box=[0, 0, 1, 1],
            detail=结果,
        )
# ========== 识别4：挑一艘"已强化满"的船（用于升级技能，逻辑与识别1相反） ==========
@AgentServer.custom_recognition("select_ship_to_upgrade")
class SelectShipToUpgrade(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        for i, 船 in enumerate(船位表):
            可强化属性, 详情 = 读一艘船详情(context, argv.image, 船["格子"])
            记录识别("select_ship_to_upgrade", f"船位{i + 1} 可强化={可强化属性 or '无'} 格子={详情}")
            # 与 enhance 相反：四个格子都没有 + / 数字（可强化属性为空）→ 视为已强化满
            if not 可强化属性:
                st.当前船名 = 读船名(context, argv.image, 船["点击框"])
                logger.info(f"选中已强化满的船：{st.当前船名}")
                return CustomRecognition.AnalyzeResult(
                    box=船["点击框"],
                    detail={"船名": st.当前船名, "状态": "已强化满", "识别详情": 详情},
                )
        记录识别("select_ship_to_upgrade", "本屏无已强化满的船")
        return CustomRecognition.AnalyzeResult(
            box=None,
            detail={"结论": "本屏无已强化满的船"},
        )
# ========== 识别5：读技能升级后的技能等级（供升级完成播报用） ==========
@AgentServer.custom_recognition("read_skill_level")
class ReadSkillLevel(CustomRecognition):
    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        roi = [1047, 345, 105, 141]
        reco = context.run_recognition(
            "读强化格子",
            argv.image,
            pipeline_override={"读强化格子": {"roi": roi}},
        )
        等级 = str(reco.best_result.text).strip() if reco and reco.hit else "未识别"
        记录识别("read_skill_level", {"技能等级": 等级})
        return CustomRecognition.AnalyzeResult(
            box=[0, 0, 1, 1],
            detail={"技能等级": 等级},
        )
# ========== 识别6：通用动态识别 —— 支持多区域、单行输出、数字校验 ==========
@AgentServer.custom_recognition("dynamic_ocr")
class DynamicOCR(CustomRecognition):
    """
    custom_recognition_param:
    {
        "base_node": "读强化格子",
        "line_format": "掉落物品：<yellow>{物品名}</yellow> 数量：<cyan>{数量}</cyan>",
        "items": [
            {
                "key": "物品名",
                "roi": [x, y, w, h],
                "digit_mode": "none",       # none / strict / loose
                "base_node": "读强化格子",    # 可选
                "expected": ["..."],          # 可选
                "threshold": 0.8,             # 可选
                "recognition": "OCR",         # 可选
                "return_text": "{key}："      # 无 line_format 时生效
            },
            {
                "key": "数量",
                "roi": [x, y, w, h],
                "digit_mode": "strict",
                "default_value": 0            # 仅 loose 模式用
            }
        ]
    }

    digit_mode:
    - "none"  ：不检查数字，命中即有效（默认）
    - "strict"：整段必须是纯阿拉伯数字（无负号、无空格、无小数点、无符号）
    - "loose" ：提取第一个数字；没数字用 default_value（默认 0），命中即有效

    detail 返回：
    {
        "texts":  {"物品名": "战利品", "数量": "5"},
        "values": {"数量": 5},
        "valid":  {"物品名": true, "数量": true}
    }
    """

    def analyze(self, context: Context, argv: CustomRecognition.AnalyzeArg):
        param_dict = json.loads(argv.custom_recognition_param) if argv.custom_recognition_param else {}
        default_base = param_dict.get("base_node", "读强化格子")
        items = param_dict.get("items", [])
        line_format = param_dict.get("line_format", "")

        if not items:
            logger.warning("dynamic_ocr: 未提供识别区域 items")
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={"texts": {}, "values": {}, "valid": {}},
            )

        文本结果 = {}
        数值结果 = {}
        有效 = {}

        for i, item in enumerate(items):
            key = item.get("key", f"区域{i + 1}")
            roi = item.get("roi")
            base_node = item.get("base_node", default_base)
            default_value = item.get("default_value", 0)
            digit_mode = item.get("digit_mode", "none")

            if not roi:
                文本结果[key] = "<未提供ROI>"
                有效[key] = False
                continue

            override = {"roi": roi}
            if "expected" in item:
                override["expected"] = item["expected"]
            if "threshold" in item:
                override["threshold"] = item["threshold"]
            if "recognition" in item:
                override["recognition"] = item["recognition"]

            reco = context.run_recognition(
                base_node,
                argv.image,
                pipeline_override={base_node: override},
            )

            if reco is not None and reco.hit:
                文字 = str(reco.best_result.text).strip()
                文本结果[key] = 文字

                if digit_mode == "strict":
                    if re.fullmatch(r"[0-9]+", 文字):
                        数值结果[key] = int(文字)
                        有效[key] = True
                    else:
                        有效[key] = False

                elif digit_mode == "loose":
                    数字匹配 = re.search(r"[0-9]+", 文字.replace(",", ""))
                    if 数字匹配:
                        数值结果[key] = int(数字匹配.group(0))
                    else:
                        数值结果[key] = default_value
                    有效[key] = True

                else:  # none
                    有效[key] = True
                    数字匹配 = re.search(r"[0-9]+", 文字.replace(",", ""))
                    if 数字匹配:
                        数值结果[key] = int(数字匹配.group(0))

            else:
                文本结果[key] = "<未命中>"
                有效[key] = False

        # ---- 输出到 UI ----
        if line_format:
            引用key = re.findall(r"\{([^{}]+)\}", line_format)
            if not 引用key or all(有效.get(k, False) for k in 引用key):
                行 = line_format
                for k in 引用key:
                    行 = 行.replace("{" + k + "}", str(文本结果.get(k, "")))
                # 关键：用 colors=True 让 loguru 解析颜色标记
                logger.opt(colors=True).info(行)
        else:
            for i, item in enumerate(items):
                key = item.get("key", f"区域{i + 1}")
                if 有效.get(key, False):
                    return_text = item.get("return_text", "{key}：").replace("{key}", key)
                    logger.info(f"{return_text}{文本结果[key]}")

        记录识别("dynamic_ocr", {"texts": 文本结果, "values": 数值结果, "valid": 有效})

        return CustomRecognition.AnalyzeResult(
            box=[0, 0, 1, 1],
            detail={
                "texts": 文本结果,
                "values": 数值结果,
                "valid": 有效,
            },
        )