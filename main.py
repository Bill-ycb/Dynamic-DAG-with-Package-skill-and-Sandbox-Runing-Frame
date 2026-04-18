# main.py
import json
import asyncio
from core.planner_llm import PlannerLLM
from core.dispatcher import AsyncDAGDispatcher

async def main():
    print("🚀 启动 [Dynamic-DAG with Auto-Packaging] 引擎")
    
    planner = PlannerLLM()
    dispatcher = AsyncDAGDispatcher()
    
    # 设计一个能触发所有架构特性的测试任务
    task = """
    请帮我执行一个终极复杂的长程混合并发任务，要求宏观并行与微观打包完美结合。请严格分析依赖关系！

    【并发分支 1：强耦合学术流水线】
    1. 检索：去 ArXiv 搜索 'Auto-Packaging DAG' 的最新学术论文。
    2. 打包清洗：拿到论文后，必须生成一个 package 节点，将以下逻辑打包顺序执行：
       - 提取论文标题和摘要。
       - 拼接成 Markdown 列表格式。
       - ⚠️ 陷阱测试：故意在代码里写一个 KeyError（例如尝试获取 data['invalid_key']）来触发自愈。
       - 将最终的 Markdown 文本赋值给 final_output。

    【并发分支 2：独立工程侦察】
    3. 检索：与分支 1 **同时**，去 GitHub 搜索 'LangGraph' 的高星开源项目。这只需作为一个独立的 atomic 节点，不需要沙盒处理。

    【阶段 3：全局汇聚与大脑发力】
    4. 研报撰写：等待【分支 1 的沙盒清洗结果】和【分支 2 的 GitHub 原始数据】都完成后，调用 `synthesize_report` 技能。将这两份数据作为上下文汇聚在一起，撰写一份主题为《DAG 引擎的学术与工程现状》的深度研报。

    【阶段 4：人工审批交付】
    5. 最后，将写好的大模型研报通过 `send_email` 发送给 cto@matrix.com，触发全局红灯拦截。

    🌟 python_sandbox (动态打包沙盒) 的代码编写铁律：
    1. 绝对不要把主逻辑封装在 `def` 函数里！请直接写平铺的执行脚本！
    2. 必须从 `deps_data` 字典中获取上游数据（不可伪造假数据）。
    3. 必须使用赋值语句将结果存入 `final_output` 变量。
    """
    
    print("🧠 Planner 正在进行拓扑编排...")
    plan_json = planner.generate_plan(task)
    print(json.dumps(plan_json, indent=2, ensure_ascii=False))
    
    final_results = await dispatcher.execute_plan(plan_json)

if __name__ == "__main__":
    asyncio.run(main())