from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context
import random


@AgentServer.custom_action("my_action_111")
class MyCustomAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        print("my_action_111 is running!")

        return True


@AgentServer.custom_action("CustomClick")
class CustomClickAction(CustomAction):
    """
    自定义点击动作，支持多种点击方式： 
        center: 点击识别区域的中心点
        留空默认: 在识别区域内随机点击
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,  
    ) -> bool:
        # 获取点击方式参数，默认为random
        # print(f"CustomClick: argv {argv}")
        click_mode = str(argv.custom_action_param).lower().strip('"')
        
        # 解析识别结果的坐标区域 [x, y, width, height]
        try:
            x, y, w, h = argv.box
        except ValueError:
            print(f"CustomClick: Invalid box format {argv.box}!")
            return False
        print(f"CustomClick: x:{x} y:{y} w:{w} h:{h}")
        print(f"CustomClick: click_mode {click_mode}, now {  click_mode == "center"}")
        # 根据点击方式计算点击坐标
        if click_mode == "center":
            # 中心点击：计算区域中心点
            click_x = x + w // 2
            click_y = y + h // 2
        else:
            # 随机点击：在区域内随机选择一点
            click_x = random.randint(x, x + w)
            click_y = random.randint(y, y + h) 
        print(f"CustomClick: Clicking at ({click_x}, {click_y}) with mode {click_mode}")
        
        # 执行点击
        click_job = context.tasker.controller.post_click(click_x, click_y)
        click_job.wait()
        
        return True
