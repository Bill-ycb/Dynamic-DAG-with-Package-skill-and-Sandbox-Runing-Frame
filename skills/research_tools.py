# skills/research_tools.py
import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()

def search_arxiv(query: str, max_results: int = 3) -> dict:
    """真实技能：检索 ArXiv 上的最新学术论文，返回结构化字典"""
    print(f"    🎓 [Skill: ArXiv] 正在检索学术论文: '{query}' ...")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    
    proxies = {
        "http": os.getenv("HTTP_PROXY"),
        "https": os.getenv("HTTPS_PROXY"),
    }
    
    try:
        response = requests.get(url, timeout=int(os.getenv("TIMEOUT", "10")), proxies=proxies)
        if response.status_code != 200:
            return {"status": "error", "message": f"ArXiv 请求失败，状态码: {response.status_code}", "results": []}
            
        root = ET.fromstring(response.text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            return {"status": "success", "message": "未找到相关的 ArXiv 论文", "results": []}
            
        results = []
        for entry in entries:
            title = entry.find('atom:title', ns).text.replace('\n', ' ').strip()
            summary = entry.find('atom:summary', ns).text.replace('\n', ' ').strip()[:150] 
            link = entry.find('atom:id', ns).text
            # 🚀 核心改动：将数据打包成结构化的字典
            results.append({
                "title": title,
                "link": link,
                "abstract": summary
            })
            
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": f"ArXiv 检索报错: {str(e)}", "results": []}

def search_github(query: str, max_results: int = 3) -> dict:
    """真实技能：检索 GitHub 上的高星开源项目，返回结构化字典"""
    print(f"    💻 [Skill: GitHub] 正在检索开源仓库: '{query}' ...")
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={max_results}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    proxies = {
        "http": os.getenv("HTTP_PROXY"),
        "https": os.getenv("HTTPS_PROXY"),
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=int(os.getenv("TIMEOUT", "10")), proxies=proxies)
        if response.status_code != 200:
            return {"status": "error", "message": f"GitHub 请求失败，状态码: {response.status_code}", "results": []}
            
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            return {"status": "success", "message": "未找到相关的 GitHub 项目", "results": []}
            
        results = []
        for item in items:
            # 🚀 核心改动：将数据打包成结构化的字典
            results.append({
                "name": item["full_name"],
                "stars": item["stargazers_count"],
                "link": item["html_url"],
                "description": item["description"] or "无描述"
            })
            
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": f"GitHub 检索报错: {str(e)}", "results": []}