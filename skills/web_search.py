# skills/web_search.py
from duckduckgo_search import DDGS

def execute_web_search(query: str, max_results: int = 3) -> str:
    """真实世界的联网搜索技能"""
    print(f"    🌐 [Skill: Web Search] 正在突破次元壁，联网搜索: '{query}' ...")
    try:
        # 使用 DDGS 发起真实的网页搜索
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "未找到相关结果。"
        
        # 将搜索到的标题和摘要拼接成字符串
        formatted = []
        for i, res in enumerate(results):
            formatted.append(f"[{i+1}] {res['title']}\n    摘要: {res['body']}")
        
        return "\n".join(formatted)
    except Exception as e:
        return f"搜索失败: {str(e)}"