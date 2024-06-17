#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Optional

from metagpt.actions.requirement_analysis.framework import (
    EvaluateFramework,
    WriteFramework,
    save_framework,
)
from metagpt.actions.requirement_analysis.trd import (
    CompressExternalInterfaces,
    DetectInteraction,
    EvaluateTRD,
    WriteTRD,
)
from metagpt.const import ASSISTANT_ALIAS
from metagpt.context import Context
from metagpt.logs import ToolLogItem, log_tool_output, logger
from metagpt.tools.tool_registry import register_tool
from metagpt.utils.cost_manager import CostManager


async def import_git_repo(url: str) -> Path:
    """
    Imports a project from a Git website and formats it to MetaGPT project format to enable incremental appending requirements.

    Args:
        url (str): The Git project URL, such as "https://github.com/geekan/MetaGPT.git".

    Returns:
        Path: The path of the formatted project.

    Example:
        # The Git project URL to input
        >>> git_url = "https://github.com/geekan/MetaGPT.git"

        # Import the Git repository and get the formatted project path
        >>> formatted_project_path = await import_git_repo(git_url)
        >>> print("Formatted project path:", formatted_project_path)
        /PATH/TO/THE/FORMMATTED/PROJECT
    """
    from metagpt.actions.import_repo import ImportRepo
    from metagpt.context import Context

    log_tool_output(
        output=[ToolLogItem(name=ASSISTANT_ALIAS, value=import_git_repo.__name__)], tool_name=import_git_repo.__name__
    )

    ctx = Context()
    action = ImportRepo(repo_path=url, context=ctx)
    await action.run()

    outputs = [ToolLogItem(name="MetaGPT Project", value=str(ctx.repo.workdir))]
    log_tool_output(output=outputs, tool_name=import_git_repo.__name__)

    return ctx.repo.workdir


async def extract_external_interfaces(acknowledge: str) -> str:
    """
    Extracts and compresses information about external system interfaces from a given acknowledgement text.

    Args:
        acknowledge (str): A natural text of acknowledgement containing details about external system interfaces.

    Returns:
        str: A compressed version of the information about external system interfaces.

    Example:
        >>> acknowledge = "## Interfaces\\n..."
        >>> external_interfaces = await extract_external_interfaces(acknowledge=acknowledge)
        >>> print(external_interfaces)
        ```json\n[\n{\n"id": 1,\n"inputs": {...
    """
    compress_acknowledge = CompressExternalInterfaces()
    return await compress_acknowledge.run(acknowledge=acknowledge)


async def mock_asearch_acknowledgement(use_case_actors: str):
    return """
## Interfaces
- 用户登录
  - Description: 用户从小程序/微应用发起请求，需要验证用户的合法身份才能正常处理。
  - ID: 1
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |authCode|用户临时免登授权码|String(64)|√||
    |loginTypeEnum|登录类型|String(20)|√||
    |authCorpId|用户所在企业/组织id|String(64)||微应用免登时传递|
    |app|应用标识|String(3)|√||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功与否，成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|用户的sessionId|string|√||
- 根据sessionId查询用户详细信息
  - Description: 查询当前用户的详细信息，如 staffId，unionId，name，avatar等信息
  - ID: 2
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |NDA_SESSION|用户sessionId|String(64)|√||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功与否，成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|用户的详细信息|object|√||
    |-> corpId|当前用户企业 钉钉ID(小程序端会拿不到该信息)|string|√||
    |-> corpName|当前用户企业名称(小程序端会拿不到该信息)|string|√||
    |-> staffId|员工在当前企业内的唯一标识，也称staffId(小程序端会拿不到该信息)|string|√||
    |-> unionId|员工在当前开发者企业账号范围内的唯一标识，系统生成，固定值，不会改变。|string|√||
    |-> name|当前用户的名称(小程序端会拿不到该信息)|string|√||
    |-> avatar|头像图片URL|string|√||
- 查询国家情况描述
  - Description: 根据国家code查询国家情况描述
  - ID: 3
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |countryCode|国家code|string|√||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|国家情况描述|object|√||
    |-> id|id|integer|√||
    |-> countryName|国家名称|string|√||
    |-> countryCode|国家code|string|√||
    |-> detail|产品法规分析|string|√||
- 查询产品法规分析（法律意见详情）
  - Description: 根据国家和业务线查询产品法规分析
  - ID: 4
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |countryCode|国家code|string|√||
    |businessCode|业务线code|string|√||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|法律意见详情|object|√||
    |-> id|id|integer|√||
    |-> countryName|国家名称|string|√||
    |-> countryCode|国家code|string|√||
    |-> businessLine|业务线|string|√||
    |-> businessCode|业务线code|string|√||
    |-> detail|产品法规分析|string|√||
    |-> signEntity|签约主体|string|√||
- 查询法律意见总数
  - Description: 法律意见总数查询
  - ID: 5
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|总数|integer|√||
- 查询所有国家和业务线信息列表
  - Description: 查询所有国家和业务线信息列表
  - ID: 6
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|所有数据列表|list of object|√||
    |-> country|国家code|string|√||
    |-> business|业务线code|string|√||
    |-> dataType|数据类型|string|√||
    |-> businessName|业务线名|string|√||
    |-> countryName|国家名|string|√||
    |-> businessNameEn|业务线名(英文)|string|√||
- 调用法务中台antlaw接口
  - ID: 7
- 国家/区域导游详情 & 法律意见详情 查询
  - Description：根据国家code查询国家/区域导游信息详情
  - ID: 8
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |countryCode|国家code|string|√||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|国家/区域导游详情|object|√||
    |-> country|||||
    |-> -> id|id|integer|√||
    |-> -> country|国家code|string|√||
    |-> -> countryName|国家中文名称|string|√||
    |-> -> countryNameEn|国家英文名称|string|√||
    |-> -> content|国家导游中文详情json数组，具体格式见下示例|list of object|√||
    |-> -> -> title|标题|object|√||
    |-> -> -> -> title|中文标题|string|||
    |-> -> -> -> titleEn|英文标题|string|||
    |-> -> -> contentList|标题下面的文字描述列表|list of object|√||
    |-> -> -> -> detail|内容中文详情|string|√||
    |-> -> -> -> detailEn|内容英文详情|string|√||
    |-> -> -> -> url|超链接|string|||
    |-> legal|法务信息|object|||
    |-> -> country|国家code|string|√||
    |-> -> businessList|业务线列表|list of object|||
    |-> -> -> id|id|integer||新增时不传，修改时传递|
    |-> -> -> business|业务线code|string|√||
    |-> -> -> businessName|业务线中文名称|string|√||
    |-> -> -> businessNameEn|业务线英文名称|string|√||
    |-> -> -> content|业务线json，具体如下|object|√||
    |-> -> -> -> detailEn|具体的详情英文内容|string|√||
    |-> -> -> -> detail|具体的详情内容|string|√||
- 国家/区域导游列表分页查询
  - Description: 分页查询国家/区域列表
  - ID: 9
  - Input Parameters:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |pageSize|分页大小|integer|√|>=1|
    |pageNum|分页大小|integer|√|>=1|
    |country|国家code|string|||
    |business|业务线code|string|||
  - Returns:
    |名称|描述|类型(长度)|必选|备注|
    | :- | :- | :-: | :- | :- |
    |success|业务处理成功true，否则false|boolean|√|只判断这个属性即可|
    |message|错误信息，可以用来提示|string|√||
    |code|返回状态码|string|√||
    |data|国家/区域导游详情|list of object|√||
    |-> id|id|integer|√||
    |-> country|国家code|string|√||
    |-> countryName|国家中文名称|string|√||
    |-> countryNameEn|国家英文名称|string|√||
    |-> gmtCreate|创建时间|string|√||
    |-> gmtModified|更新时间|string|√||
    |total|数据总量|integer|√||

    """


@register_tool(tags=["system design", "write trd", "Write a TRD"])
async def write_trd(
    use_case_actors: str,
    user_requirements: str,
    investment: float = 10,
    context: Optional[Context] = None,
) -> (str, str):
    """
    Handles the writing of a Technical Requirements Document (TRD) based on user requirements.

    Args:
        user_requirements (str): The new/incremental user requirements.
        use_case_actors (str): Description of the actors involved in the use case.
        investment (float): Budget. Automatically stops optimizing TRD when the budget is overdrawn.
        context (Context, optional): The context configuration. Default is None.
    Returns:
        str: The newly created TRD.

    Example:
        >>> # Given a new user requirements, write out a new TRD.
        >>> user_requirements = "Write a 'snake game' TRD."
        >>> use_case_actors = "- Actor: game player;\\n- System: snake game; \\n- External System: game center;"
        >>> investment = 10.0
        >>> trd = await write_trd(
        >>>     user_requirements=user_requirements,
        >>>     use_case_actors=use_case_actors,
        >>>     investment=investment,
        >>> )
        >>> print(trd)
        ## Technical Requirements Document\n ...
    """
    context = context or Context(cost_manager=CostManager(max_budget=investment))
    compress_acknowledge = CompressExternalInterfaces()
    acknowledgement = await mock_asearch_acknowledgement(use_case_actors)  # Replaced by acknowledgement_repo later.
    external_interfaces = await compress_acknowledge.run(acknowledge=acknowledgement)
    detect_interaction = DetectInteraction(context=context)
    w_trd = WriteTRD(context=context)
    evaluate_trd = EvaluateTRD(context=context)
    is_pass = False
    evaluation_conclusion = ""
    interaction_events = ""
    trd = ""
    while not is_pass and (context.cost_manager.total_cost < context.cost_manager.max_budget):
        interaction_events = await detect_interaction.run(
            user_requirements=user_requirements,
            use_case_actors=use_case_actors,
            legacy_interaction_events=interaction_events,
            evaluation_conclusion=evaluation_conclusion,
        )
        trd = await w_trd.run(
            user_requirements=user_requirements,
            use_case_actors=use_case_actors,
            available_external_interfaces=external_interfaces,
            evaluation_conclusion=evaluation_conclusion,
            interaction_events=interaction_events,
            previous_version_trd=trd,
        )
        evaluation = await evaluate_trd.run(
            user_requirements=user_requirements,
            use_case_actors=use_case_actors,
            trd=trd,
            interaction_events=interaction_events,
        )
        is_pass = evaluation.is_pass
        evaluation_conclusion = evaluation.conclusion

    return trd


@register_tool(tags=["system design", "write software framework", "Write a software framework based on a TRD"])
async def write_framework(
    use_case_actors: str,
    trd: str,
    additional_technical_requirements: str,
    output_dir: Optional[str] = "",
    investment: float = 15.0,
    context: Optional[Context] = None,
) -> str:
    """
    Run the action to generate a software framework based on the provided TRD and related information.

    Args:
        use_case_actors (str): Description of the use case actors involved.
        trd (str): Technical Requirements Document detailing the requirements.
        additional_technical_requirements (str): Any additional technical requirements.
        output_dir (str, optional): Path to save the software framework files. Default is en empty string.
        investment (float): Budget. Automatically stops optimizing TRD when the budget is overdrawn.
        context (Context, optional): The context configuration. Default is None.

    Returns:
        str: The generated software framework as a string of pathnames.

    Example:
        >>> use_case_actors = "- Actor: game player;\\n- System: snake game; \\n- External System: game center;"
        >>> trd = "## TRD\\n..."
        >>> additional_technical_requirements = "Using Java language, ..."
        >>> investment = 15.0
        >>> framework = await write_framework(
        >>>    use_case_actors=use_case_actors,
        >>>    trd=trd,
        >>>    additional_technical_requirements=constraint,
        >>>    investment=investment,
        >>> )
        >>> print(framework)
        [{"path":"balabala", "filename":"...", ...
    """
    context = context or Context(cost_manager=CostManager(max_budget=investment))
    write_framework = WriteFramework(context=context)
    evaluate_framework = EvaluateFramework(context=context)
    is_pass = False
    framework = ""
    evaluation_conclusion = ""
    acknowledgement = await mock_asearch_acknowledgement(use_case_actors)  # Replaced by acknowledgement_repo later.
    while not is_pass and (context.cost_manager.total_cost < context.cost_manager.max_budget):
        try:
            framework = await write_framework.run(
                use_case_actors=use_case_actors,
                trd=trd,
                acknowledge=acknowledgement,
                legacy_output=framework,
                evaluation_conclusion=evaluation_conclusion,
                additional_technical_requirements=additional_technical_requirements,
            )
        except Exception as e:
            logger.info(f"{e}")
            break
        evaluation = await evaluate_framework.run(
            use_case_actors=use_case_actors,
            trd=trd,
            acknowledge=acknowledgement,
            legacy_output=framework,
            additional_technical_requirements=additional_technical_requirements,
        )
        is_pass = evaluation.is_pass
        evaluation_conclusion = evaluation.conclusion

    file_list = await save_framework(dir_data=framework, output_dir=output_dir)
    logger.info(f"Output:\n{file_list}")
    return "## Software Framework" + "".join([f"\n- {i}" for i in file_list])
