from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("US_Stock_Agent")

@mcp.tool()
def get_daily_market_summary() -> str:
    """
    当需要分析今日美股走势、评估宏观风险、或者查看 VIX 恐慌指数时，必须调用此工具。
    它会返回真实的标普、纳指、道指以及 VIX 的最新点位和涨跌幅。
    """
    targets = {
        "标普500指数 (SPY)": "^GSPC",
        "纳斯达克指数 (QQQ)": "^IXIC",
        "道琼斯指数 (DIA)": "^DJI",
        "VIX 恐慌指数": "^VIX"
    }

    report_lines = ["📊 【今日美股与宏观市场核心数据】\n"]

    for name, ticker_symbol in targets.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period='5d')

            if len(hist) >= 2:
                latest_close = hist['Close'].iloc(-1)
                prev_close = hist['Close'].iloc(-2)
                pct_change = ((latest_close-prev_close)/prev_close)*100

                trend = "📈 上涨" if pct_change > 0 else "📉 下跌"
                line = f"- {name}:最新点位 {latest_close:.2f} | 较前一交易日 {trend} {abs(pct_change):.2f}%"

                if ticker_symbol == "^VIX":
                    if latest_close > 25.0:
                        line += " ⚠️ (警告：VIX 处于高位，市场恐慌情绪蔓延，流动性可能收紧)"
                    
                    elif latest_close < 15.0:
                        line += " 🟢 (提示：VIX 处于低位，市场情绪平稳，风险偏好较高)"
                
                report_lines.append(line)
            
            else:
                report_lines.append(f"- {name}: 暂无足够数据")
            
        except Exception as e:
            report_lines.append(f"- {name}: 数据获取失败 ({str(e)})")
    
    return "\n".join(report_lines)

if __name__ == "__main__":
    mcp.run()