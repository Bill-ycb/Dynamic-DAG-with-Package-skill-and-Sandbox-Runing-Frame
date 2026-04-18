# skills/sandbox.py
import sys
import io
import traceback
import copy
import re  # 🚀 新增正则表达式库，用于强力清洗大模型输出
from openai import OpenAI

def fix_code_with_reflexion(failed_code: str, error_trace: str, intent: str) -> str:
    """内部的反思大脑：专门负责看懂报错并修 Bug，自带结果清洗器"""
    print(f"      📞 [Reflexion API] 正在将报错信息发送给反思大脑...")
    client = OpenAI(
        api_key="sk-b186038b69864b678da78736993ac0f3",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 🧠 优化 Prompt：引导它使用标准的 Markdown 格式包裹代码
    prompt = f"""意图：{intent}
报错：{error_trace}
原代码：
{failed_code}

请修复 Bug。
【沙盒环境铁律】：
1. 绝对不许伪造、Mock 或硬编码假数据！
2. 缺失的输入数据必须从名为 `deps_data` 的字典中获取（例如：data = deps_data.get('node_id')）。
3. 最终结果必须赋值给 `final_output` 变量。
【严格输出规则】：你可以简短解释，但修复后的完整 Python 代码必须且只能放在一对 ```python 和 ``` 之间！千万不要漏掉代码块标记！"""
    
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    reply_text = response.choices[0].message.content.strip()
    
    # ✂️ 强力正则清洗器：无视所有自然语言，精准提取代码
    # re.DOTALL 允许 '.' 匹配包括换行符在内的所有字符
    match = re.search(r'```(?:python)?\s*(.*?)```', reply_text, re.DOTALL)
    if match:
        clean_code = match.group(1).strip()
        print(f"      ✂️ [清洗器] 成功过滤大模型的自然语言，精准提取纯代码！")
        return clean_code
    else:
        # 如果大模型完全没有使用 ``` 标记，做最后的容错尝试
        print(f"      ⚠️ [清洗器警告] 未检测到标准 Markdown 代码块，尝试原样返回。")
        return reply_text.strip()

def run_python_sandbox(code: str, deps_data: dict, intent: str = "处理数据", max_retries: int = 3) -> str:
    """具备状态快照与 Reflexion 自愈能力的动态沙盒"""
    print("\n" + "-"*40)
    print(f"📦 [沙盒节点启动] 意图: {intent}")
    
    # 💥 获取初始状态的不可变快照 (Snapshot)
    state_snapshot = copy.deepcopy(deps_data)
    print(f"📸 [架构特性: 状态快照] 已深拷贝上游依赖数据 (大小: {len(str(deps_data))} 字符)，准备安全隔离...")
    print("-" * 40)
    
    current_code = code
    
    for attempt in range(1, max_retries + 1):
        print(f"\n      ▶️ [沙盒执行尝试 {attempt}/{max_retries}]")
        
        # 💥 每次尝试前，从快照恢复纯净状态 (Rollback)
        clean_deps = copy.deepcopy(state_snapshot)
        local_vars = {"deps_data": clean_deps, "final_output": None}
        print(f"      🔄 [架构特性: 状态回滚] 已从快照恢复纯净的局部变量环境 (deps_data, final_output)。")
        print(f"      💻 [注入代码]:\n{'-'*30}\n{current_code}\n{'-'*30}")
        
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            exec(current_code, {}, local_vars)
            sys.stdout = old_stdout 
            print(f"      🟢 [沙盒成功] 代码跑通，无报错抛出！")
            return local_vars.get("final_output", "执行成功但未赋值 final_output")
            
        except Exception as e:
            sys.stdout = old_stdout 
            error_trace = traceback.format_exc()
            print(f"      🚨 [沙盒崩溃] 捕获到异常：\n{str(e)}\n")
            print(f"      🛡️ [脏数据拦截] 异常抛出，当前局部的 `deps_data` 污染已被丢弃！")
            
            if attempt < max_retries:
                print(f"      🧠 [架构特性: 自我修复] 启动 Reflexion 反思引擎...")
                current_code = fix_code_with_reflexion(current_code, error_trace, intent)
                print(f"      🔧 [补丁生成完毕] 准备进入下一轮执行。")
            else:
                return f"❌ 沙盒最终失败，已耗尽 {max_retries} 次修复机会。\n{error_trace}"


