# -*- coding: utf-8 -*-
import json
from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import enhance_state as st
from logger import logger
def 取识别detail(reco) -> dict:
    """把自定义识别的 best_result.detail 统一解析成 dict，兼容多层 JSON 字符串。"""
    if not reco or not reco.hit or reco.best_result is None:
        return {}
    d = reco.best_result.detail
    for _ in range(3):
        if isinstance(d, dict):
            return d
        if isinstance(d, str) and d:
            d = json.loads(d)
        else:
            break
    return d if isinstance(d, dict) else {}
# ========== 动作0：任务开始时重置记忆 ==========
@AgentServer.custom_action("reset_enhance_state")
class ResetEnhanceState(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        st.重置()
        return True
# ========== 动作1：读素材数值后做决定 ==========
@AgentServer.custom_action("judge_material")
class JudgeMaterial(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        reco = context.run_recognition(
            "读素材数值并判断",
            context.tasker.controller.cached_image,
        )
        数值 = 取识别detail(reco)
        # 强化前：能强化但自动选择后数值=0 → 该属性素材耗尽（只播报新增的）
        新耗尽 = [
            a for a in st.当前船可强化属性
            if 数值.get(a, 0) == 0 and a not in st.已耗尽属性
        ]
        st.已耗尽属性.update(新耗尽)
        for 属性名 in 新耗尽:
            logger.info(f"{属性名}属性素材已耗尽")
        if set(st.属性列表) <= st.已耗尽属性:
            context.override_next(argv.node_name, ["返回选船界面3"])
            return True
        这船还能强化 = any(
            a not in st.已耗尽属性 and 数值.get(a, 0) > 0
            for a in st.当前船可强化属性
        )
        if 这船还能强化:
            context.override_next(argv.node_name, ["点确定进强化确认"])
        else:
            context.override_next(argv.node_name, ["返回选船界面2"])
        return True
# ========== 动作2：读强化确认结果后做决定 + 日志播报 ==========
@AgentServer.custom_action("judge_enhance_result")
class JudgeEnhanceResult(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        reco = context.run_recognition(
            "读强化结果并判断",
            context.tasker.controller.cached_image,
        )
        结果 = 取识别detail(reco)
        # 能强化但强化后仍非 MAX（含 OCR 漏读）→ 该素材不足以顶满，判定耗尽
        未满属性 = [a for a in st.当前船可强化属性 if 结果.get(a) != "MAX"]
        新耗尽 = [a for a in 未满属性 if a not in st.已耗尽属性]
        st.已耗尽属性.update(未满属性)
        for 属性名 in 新耗尽:
            logger.info(f"{属性名}属性素材已耗尽")
        强化满 = bool(st.当前船可强化属性) and not 未满属性
        提示 = f"{st.当前船名}：{'可强化属性已强化满' if 强化满 else '可强化属性未强化满'}"
        logger.info(提示)
        return True
# ========== 动作3：技能升级完成后的日志播报（含技能等级） ==========
@AgentServer.custom_action("report_upgrade_done")
class ReportUpgradeDone(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        reco = context.run_recognition(
            "技能升级完成播报",
            context.tasker.controller.cached_image,
        )
        等级 = 取识别detail(reco).get("技能等级", "未识别")
        logger.info(f"{st.当前船名}：技能升级完成（当前等级 {等级}）")
        return True