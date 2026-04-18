# core/dispatcher.py
import asyncio
from skills.research_tools import search_arxiv, search_github
from skills.sandbox import run_python_sandbox

# 模拟的红灯技能
def send_email_mock(args, deps_data):
    return f"✅ 邮件已成功发送至：{args.get('to')}"

SKILL_REGISTRY = {
    "search_arxiv": lambda args, deps_data: search_arxiv(args.get("query", "AI")),
    "search_github": lambda args, deps_data: search_github(args.get("query", "AI")),
    "send_email": send_email_mock
}

class AsyncDAGDispatcher:
    async def _simulate_async_hitl(self, node_id: str, skill_name: str) -> bool:
        """模拟无阻塞的异步人类审批"""
        print(f"\n  ⏸️  [HITL 挂起] 节点 {node_id} ({skill_name}) 触发红灯工具拦截！")
        print(f"      [系统提示] 正在等待前端 UI 人工授权 (模拟耗时 3 秒) ...")
        print(f"      [系统提示] ⚠️ 请注意：当前事件循环未阻塞，其他并行的绿灯节点可以继续狂飙！\n")
        
        await asyncio.sleep(3) 
        
        print(f"  ▶️  [HITL 通过] 收到人类授权，节点 {node_id} 恢复后台执行！")
        return True

    async def _execute_node(self, node: dict, deps_data: dict) -> tuple:
        node_id = node["node_id"]
        node_type = node.get("node_type", "atomic")

        if node.get("require_hitl", False):
            approved = await self._simulate_async_hitl(node_id, node.get("skill_name", "unknown"))
            if not approved:
                return node_id, "🚫 人工拒绝执行"

        # 根据节点类型分配任务
        if node_type == "atomic":
            skill_name = node["skill_name"]
            print(f"  ⚙️ [Worker 启动] 节点 {node_id} 开始执行 Atomic 技能: {skill_name}")
            func = SKILL_REGISTRY.get(skill_name)
            result = await asyncio.to_thread(func, node.get("skill_args", {}), deps_data)
            
        elif node_type == "package":
            print(f"  📦 [Worker 启动] 节点 {node_id} 准备将代码送入 Sandbox 容器执行...")
            result = await asyncio.to_thread(
                run_python_sandbox, 
                node.get("package_code", ""), 
                deps_data, 
                node.get("package_intent", "数据处理")
            )
            
        print(f"  🟢 [Worker 完成] 节点 {node_id} 返回了结果。")
        return node_id, result

    async def execute_plan(self, plan: dict) -> dict:
        nodes = plan.get("dag_nodes", [])
        completed = set()
        results = {}
        running_tasks = {}

        print("\n" + "="*50)
        print("🔄 [阶段 2: 动态 DAG 引擎调度] 点火执行")
        print("="*50)

        # 真正的异步 DAG 调度循环
        while len(completed) < len(nodes):
            print(f"\n🔍 [拓扑扫描] 引擎正在扫描 DAG (已完成: {len(completed)}/{len(nodes)})...")
            
            batch_added = False
            for node in nodes:
                node_id = node["node_id"]
                if node_id not in completed and node_id not in running_tasks:
                    deps = node.get("depends_on", [])
                    # 检查前置依赖是否全部满足
                    if all(dep in completed for dep in deps):
                        print(f"    🚀 发现就绪节点 [{node_id}] (依赖 {deps} 已满足)，加入并发池！")
                        deps_data = {dep: results[dep] for dep in deps}
                        task = asyncio.create_task(self._execute_node(node, deps_data))
                        running_tasks[node_id] = task
                        batch_added = True

            if not batch_added and not running_tasks:
                print("🚨 出现死锁：没有新节点可加，也没有运行中的任务。")
                break 

            print(f"⚡ [当前并发状态] 正在同时执行 {len(running_tasks)} 个分支任务...")
            
            # 等待任意一个（或多个）并行任务完成
            done, pending = await asyncio.wait(
                running_tasks.values(), 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 收割完成的任务
            for task in done:
                node_id = next(nid for nid, t in running_tasks.items() if t == task)
                _, res = task.result()
                results[node_id] = res
                completed.add(node_id)
                del running_tasks[node_id]
                print(f"✅ [节点收割] 引擎已记录节点 {node_id} 的状态。")

                # 🚀 === 新增：保姆级数据监控面板 ===
                print(f"   📊 [产出数据预览 | Node: {node_id}]:")
                res_str = str(res)
                
                # 如果数据太长，截断它，防止刷屏
                MAX_LENGTH = 300 
                if len(res_str) > MAX_LENGTH:
                    display_text = res_str[:MAX_LENGTH] + f"\n\n... (原始数据长达 {len(res_str)} 字符，为保持终端整洁已截断)"
                else:
                    display_text = res_str
                    
                # 画一个优雅的边框把内容框起来
                print("   ┌" + "─" * 60)
                for line in display_text.split('\n'):
                    # 避免空行导致边框断裂
                    print(f"   │ {line}")
                print("   └" + "─" * 60 + "\n")
                # ==================================



        print("\n" + "="*50)
        print("🎉 [阶段 3: 执行完毕] DAG 引擎平稳降落！")
        print("="*50)
        return results