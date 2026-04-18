# core/planner_llm.py
import json
from openai import OpenAI

class PlannerLLM:
    def __init__(self):
        self.client = OpenAI(
            api_key="sk-b186038b69864b678da78736993ac0f3", 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen3.6-plus-2026-04-02"
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "submit_dynamic_dag",
                    "description": "提交动态 DAG 执行计划。根据任务耦合度决定使用原子节点拆分，还是打包节点组合。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dag_nodes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "node_id": {"type": "string"},
                                        "node_type": {
                                            "type": "string",
                                            "enum": ["atomic", "package"],
                                            "description": "如果调用单一工具选 atomic；如果涉及复杂的数据处理、多步清洗，选 package"
                                        },
                                        "depends_on": {
                                            "type": "array", 
                                            "items": {"type": "string"}
                                        },
                                        "skill_name": {"type": "string", "enum": ["search_arxiv", "search_github", "send_email"]},
                                        "skill_args": {"type": "object"},
                                        "require_hitl": {"type": "boolean", "description": "红灯工具必须设为 true"},
                                        "package_intent": {"type": "string"},
                                        "package_code": {"type": "string"}
                                    },
                                    "required": ["node_id", "node_type", "depends_on"]
                                }
                            }
                        },
                        "required": ["dag_nodes"]
                    }
                }
            }
        ]

    def generate_plan(self, user_task: str) -> dict:
        print("\n" + "="*50)
        print("🧠 [阶段 1: Planner 智能编排] 启动")
        print("="*50)
        print(f"🗣️  接收到用户任务:\n{user_task}\n")
        print("🤔  正在思考如何拆解（原子化并行）和打包（代码沙盒）...")
        
        messages = [
            {"role": "system", "content": """你是一个遵循【动态 DAG 与自动打包】架构的规划器。
            【拆分 vs 打包 规则】：
            1. 拆分 (Split)：对于独立的 API 调用（如并发搜索），生成并行的 `atomic` 节点。
            2. 打包 (Package)：对于耦合的数据清洗、聚合操作，不要生成多个节点，而是生成一个 `package` 节点，将逻辑写在 Python 代码中。
            3. 汇聚 (Many-to-One)：如果 C 需要 A 和 B 的结果，将 A,B 设为并行的 atomic，将 C 设为 package 并 depends_on: [A, B]。
            """},
            {"role": "user", "content": user_task}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto", 
                temperature=0.1 
            )
            tool_call = response.choices[0].message.tool_calls[0]
            args_str = tool_call.function.arguments
            plan_json = json.loads(args_str)
            
            print("✅  Planner 编排完成！生成的动态拓扑结构如下:")
            # 使用高亮打印让不同类型的节点一目了然
            for node in plan_json.get("dag_nodes", []):
                t = node.get("node_type")
                icon = "📦" if t == "package" else "⚙️"
                deps = f"依赖: {node.get('depends_on')}" if node.get('depends_on') else "无依赖 (可立即执行)"
                print(f"    {icon} 节点 [{node['node_id']}] ({t}) | {deps}")
                
            return plan_json
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return {}