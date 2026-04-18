# skills/report_writer.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def write_report_with_llm(topic: str, context_data: dict) -> str:
    """真实技能：调用大模型阅读抓取的数据，并撰写 Markdown 研报"""
    print(f"    🧠 [Skill: Report Writer] 正在召唤大模型阅读数据并撰写: '{topic}' ...")
    
    # 初始化 Qwen 作为写稿大脑
    llm = ChatOpenAI(
        model="qwen3.6-plus-2026-04-02", 
        api_key="sk-b186038b69864b678da78736993ac0f3",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    # 设计强大的提示词，强制它基于我们抓回来的数据写稿
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个资深的 AI 行业研究员。
        请严格根据我提供的【原始抓取数据】，撰写一份结构清晰、排版精美的 Markdown 研究报告。
        
        写作规则：
        1. 必须包含标题、摘要、开源项目分析、学术论文分析。
        2. 不要编造数据，只能使用提供的信息。
        3. ⚠️ 如果某项数据提示“报错”、“失败”或“超时”，请在报告的【风险与局限性】部分客观指出该数据缺失。
        """),
        ("user", "报告主题：{topic}\n\n以下是我用爬虫为你抓取的原始数据：\n{context_data}\n\n请直接输出 Markdown 报告正文。")
    ])
    
    try:
        # 将字典数据转为字符串喂给大模型
        chain = prompt | llm
        response = chain.invoke({
            "topic": topic, 
            "context_data": str(context_data)
        })
        return response.content
    except Exception as e:
        return f"撰写报告失败: {str(e)}"