from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("my_reco_222")
class MyRecongition(CustomRecognition):

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        print("some thing fun?")
        print(CustomRecognition.AnalyzeResult(
            box=(1033, 582, 81, 46), detail="Ex"
        ))
        # reco_detail = context.run_recognition(
        #     "识别Ex",
        #     argv.image,
        #     pipeline_override={"识别Ex": {"roi": [1033, 582, 81, 46]}},
        # )
        # print(reco_detail)

        return CustomRecognition.AnalyzeResult(
            box=(1033, 582, 81, 46), detail="Ex"
        )
