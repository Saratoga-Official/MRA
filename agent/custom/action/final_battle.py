import re
import json
import time

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger


@AgentServer.custom_action("final_battle_ex_select")
class final_battle_ex_select(CustomAction):
    """
    go to seleted final battle ex

    param:
    {
        "want_to": "want_to_ex_num"
    }
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:

        want_to_num = int(json.loads(argv.custom_action_param)["want_to"])

        img = context.tasker.controller.post_screencap().wait().get()
        reco_detail = context.run_recognition(
            entry="Ex_select",
            image=img,
        )
        if reco_detail is not None:
            cur_num = int(reco_detail.best_result.text[-1])
            logger.debug(f"type of cur: {type(cur_num)}")
            logger.debug(f"type of want: {type(want_to_num)}")
            delta_num = want_to_num - cur_num # e.g. want to Ex1, cur is Ex2, delta_num is -1
            left_click_pos = (1040, 670)
            right_click_pos = (1190, 670)
            logger.info(f"want to Ex-{want_to_num}, current Ex-{cur_num}")
            if delta_num > 0:
                for _ in range(delta_num):
                    context.tasker.controller.post_click(*right_click_pos).wait()
                    time.sleep(1)
            elif delta_num < 0:
                for _ in range(-delta_num):
                    context.tasker.controller.post_click(*left_click_pos).wait()
                    time.sleep(1)
            else:
                pass
        else:
            logger.error("can't catch current Ex num")
            return CustomAction.RunResult(success=False)
        
        return CustomAction.RunResult(success=True)