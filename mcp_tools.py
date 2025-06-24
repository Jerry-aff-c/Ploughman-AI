import random
from fastmcp import FastMCP
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import traceback
from util.modelRequestApi import quick_call as call_api
from util.MYSQLInquiry import MysqlQuery as RealMysqlQuery

# 初始化MCP服务器
mcp = FastMCP(
    name="PloughmanAI工具服务",
    instructions="PloughmanAI工具服务提供数据查询、数据库操作和可视化等功能"
)


# 基础工具：获取某人的下班时间（模拟功能）
@mcp.tool()
def get_time(name: str) -> str:
    """模拟获取某人的下班时间"""
    choices = ["6.00 PM", "7.00 PM", "8.30 PM"]
    backoff = random.choice(choices)
    return f"{name} 今天预计 {backoff} 下班"


# 分析工具：根据生辰八字分析财运
@mcp.tool()
def analyze_fortune(birthday_data: dict) -> str:
    """调用模型分析生辰八字对应的财运信息"""
    prompt = (
        f"根据中国传统风水学，分析以下生辰八字对应的财运和发展前景：{birthday_data}\n"
        f"请详细说明命主的财富运势和发展趋势。"
    )
    response = call_api(
        user_content=prompt,
        model_type="local",
        model="deepseek-r1-0528-qwen3-8b"
    )
    return response


# 数据库工具：查看指定数据库中的所有表
@mcp.tool()
def show_tables(database: str) -> dict:
    """查询指定数据库中的所有表"""
    try:
        cfg = next((c for c in load_db_configs() if c["database"] == database), None)
        if not cfg:
            return {"error": f"未找到数据库配置：{database}"}

        mysql = RealMysqlQuery(
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            host=cfg.get("host", "localhost"),
            port=cfg.get("port", 3306),
        )

        # 执行SHOW TABLES查询
        result = mysql.query("SHOW TABLES")

        # 提取表名
        tables = []
        if result and isinstance(result, list) and len(result) > 0:
            key = list(result[0].keys())[0]
            tables = [row[key] for row in result]

        return {"database": database, "tables": tables}
    except Exception as e:
        return {"error": f"查询失败: {str(e)}", "trace": traceback.format_exc()}


# 数据库工具：创建新表
@mcp.tool()
def create_table(table_name: str, columns: dict) -> str:
    """在指定数据库中创建新表"""
    try:
        cfg = load_db_configs()[0]

        mysql = RealMysqlQuery(
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            host=cfg.get("host", "localhost"),
            port=cfg.get("port", 3306),
        )

        # 构建CREATE TABLE SQL
        columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        create_sql = f"CREATE TABLE {table_name} ({columns_sql})"

        # 执行创建表命令
        mysql.execute(create_sql)
        return f"表 {table_name} 创建成功"
    except Exception as e:
        return f"创建表失败: {str(e)}"


# 数据库工具：执行SQL查询
@mcp.tool()
def execute_query(sql: str) -> dict:
    """执行任意SQL查询并返回结果"""
    results = {}

    for cfg in load_db_configs():
        try:
            mysql = RealMysqlQuery(
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                host=cfg.get("host", "localhost"),
                port=cfg.get("port", 3306),
            )

            result = mysql.query(sql)
            results[cfg["database"]] = result
        except Exception as e:
            results[cfg["database"]] = {"error": str(e), "trace": traceback.format_exc()}

    return results


# 数据库工具：将数据可视化
@mcp.tool()
def visualize_data(data: list, chart_type: str = "line") -> str:
    """将数据可视化为图表"""
    try:
        # 准备数据
        df = pd.DataFrame(data)
        if df.empty:
            return "无数据可可视化"

        # 创建图表
        plt.figure(figsize=(10, 6))

        if chart_type == "bar":
            df.iloc[:, 0].value_counts().plot(kind='bar')
        elif chart_type == "pie":
            df.iloc[:, 0].value_counts().plot(kind='pie', autopct='%1.1f%%')
        else:  # 默认折线图
            if len(df.columns) >= 2:
                df.plot(x=df.columns[0], y=df.columns[1], kind='line')
            else:
                df.iloc[:, 0].plot(kind='line')

        plt.title(f"数据可视化 ({chart_type}图)")
        plt.grid(True)

        # 保存图表到内存
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        return f"可视化失败: {str(e)}"


# 加载数据库配置
def load_db_configs() -> list:
    """加载数据库连接配置"""
    return [
        {
            "user": "test_user",
            "password": "test_pass",
            "database": "test_database",
            "host": "192.168.2.60",
            "port": 3306,
        },
        {
            "user": "admin",
            "password": "admin_pass",
            "database": "information_schema",
            "host": "192.168.2.60",
            "port": 3306,
        },
    ]


if __name__ == "__main__":
    # 启动MCP工具服务
    mcp.run(
        transport="sse",  # 使用SSE协议
        host="localhost",
        port=8000,
        log_level="debug"
    )