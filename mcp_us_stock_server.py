from mcp.server.fastmcp import FastMCP
import os 
import requests

mcp = FastMCP("US_Stock_Agent")

@mcp.tool()
def get_daily_market_summary():
    # 1. 从云端环境中提取你的专属通行证
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return "数据系统异常：未在环境变量中检测到 FMP_API_KEY，请检查 Render 配置。"

    # 2. 锁定你要监控的核心标的（完美包含 VIX 恐慌指数）
    symbols = ["SPY", "QQQ", "DIA", "^VIX"]
    market_data = {}

    try:
        # 3. 逐个向 FMP 发起极其正规的 API 问询
        for sym in symbols:
            # 构建正规军专属的请求 URL
            url = f"https://financialmodelingprep.com/api/v3/quote/{sym}?apikey={api_key}"
            
            # 设置 10 秒超时，防止网络卡死
            response = requests.get(url, timeout=10)
            data = response.json()

            if data and len(data) > 0:
                info = data[0]
                market_data[sym] = {
                    "当前价格": info.get("price"),
                    "日内涨跌幅": f"{info.get('changesPercentage')}%",
                    "今日最高": info.get("dayHigh"),
                    "今日最低": info.get("dayLow"),
                    "成交量": info.get("volume")
                }
            else:
                market_data[sym] = "数据提供商未能返回该标的有效数据"

        # 4. 将结构化数据组装成 DeepSeek 大脑最喜欢的格式
        report_text = "【底层 API 实时数据源已切入】\n今日美股及波动率核心观测数据如下：\n"
        for sym, details in market_data.items():
            report_text += f"- {sym}: {details}\n"

        return report_text

    except Exception as e:
        return f"底层数据 API 请求物理崩溃，错误信息: {str(e)}"

if __name__ == "__main__":
    mcp.run()