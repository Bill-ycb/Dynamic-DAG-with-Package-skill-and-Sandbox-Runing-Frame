# core/memory_llm.py
import os
from openai import OpenAI

class MemoryLLM:
    def __init__(self, system_prompt: str = "你是一个乐于助人的 AI 助手。"):
        # 1. 初始化客户端
        self.client = OpenAI(
            api_key="sk-b186038b69864b678da78736993ac0f3", 
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.model = "qwen3.6-plus-2026-04-02"
        
        # 2. 初始化核心记忆数组（第一条永远是 system 人设）
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]

    def chat(self, user_input: str) -> str:
        """接收用户输入，产生回复，并自动管理记忆"""
        
        # 1. 将用户的最新提问追加到记忆中
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            # 2. 将包含所有历史记录的完整记忆发送给大模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7
            )
            
            # 3. 提取大模型的回复文本
            assistant_reply = response.choices[0].message.content
            
            # 4. 【关键步骤】将大模型的回复也追加到记忆中！
            self.messages.append({"role": "assistant", "content": assistant_reply})
            
            return assistant_reply
            
        except Exception as e:
            # 如果中途报错（比如断网），我们需要把刚刚加进去的用户提问弹出来，保持记忆的整洁
            self.messages.pop()
            return f"Error: 呼叫大模型失败 ({str(e)})"
            
    def get_history_length(self) -> int:
        """获取当前记忆的轮数（排除 system）"""
        return len(self.messages) - 1