from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context


@AgentServer.custom_action("final_battle_ex_select")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        # prev_boxes = argv.reco_detail.boxes
        # print(prev_boxes)
        # clicked_node = context.run_action(
        #     entry="Ê¶±ðEx",
        #     box=[ 1033, 582, 81, 46 ]
        # )
        print("final_battle_ex_select is running!")
        return True

        # if clicked_node is not None:
        #     return CustomAction.RunResult(success=True)
        # else:
        #     return CustomAction.RunResult(success=False)
