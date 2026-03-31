# services.py
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 加载环境变量
load_dotenv()
api_key = os.getenv("my_llm_key")

# 初始化 DeepSeek 大脑
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com" 
)

async def generate_daily_investment_report() -> str:

    print("🔌 Python 正在直接调动 MCP 底层工具获取数据...")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_us_stock_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("🛠️ 正在抓取华尔街真实数据...")
            tool_result = await session.call_tool("get_daily_market_summary", {})
            real_market_data = tool_result.content[0].text
            print("✅ 数据抓取成功！正在将现实交给大模型撰写报告...")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是一位华尔街顶级的宏观对冲基金经理。你的任务是根据用户提供的【真实市场数据】分析当天的美股与宏观市场。\n"
                        "请严格按照以下结构输出 Markdown 格式的投资报告：\n"
                        "1. 📊 盘面总结\n"
                        "2. ⚠️ 宏观风险评估 (重点结合 VIX 恐慌指数判断市场的流动性与风险偏好)\n"
                        "3. 💡 明日操作建议 (给出极其明确的加仓、减仓、对冲或观望建议，不要模棱两可)\n"
                        "语气要极其专业、冷酷、客观，充满华尔街精英的风格。"
                    )
                },
                {
                    "role": "user",
                    "content": f"这是今天刚出炉的真实市场数据，请立刻基于此生成深度投资报告：\n\n{real_market_data}"
                }
            ]

            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            
            return response.choices[0].message.content