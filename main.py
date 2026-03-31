import os
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services import generate_daily_investment_report

app = FastAPI(title="US-Stock-Agent-Api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

async def scheduled_report_job():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"\n⏰ [定时任务触发] 开始生成 {today_str} 的华尔街市场报告...")

    try:
        report_content = await generate_daily_investment_report()
        filename = f"{REPORTS_DIR}/market_report_{today_str}.md"
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ [大功告成] 报告已成功保存至本地文件夹：{filename}")
    
    except Exception as e:
        print(f"❌ [任务失败] Agent 运行出现异常: {e}")
    
@app.on_event("startup")
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_report_job, 'cron', day_of_week='mon-fri', hour=16, minute=30)
    scheduler.start()
    print("⏱️ 华尔街 Agent 定时调度引擎已启动！(每日 16:30 将自动执行)")

@app.get("/generate_now")
async def generate_now():
    print("⚡ 接收到手动触发指令，Agent 启动...")
    report = await generate_daily_investment_report()
    return {"status": "success", "date": str(datetime.date.today()), "report": report}

@app.get("/latest_report")
async def get_latest_report():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{REPORTS_DIR}/market_report_{today_str}.md"
    
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "report": content}
    else:
        return {"status": "pending", "message": "今天的报告还未生成，请稍后再试或手动触发。"}