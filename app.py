import gradio as gr
import asyncio
from agents.scheduler_agent import SchedulerAgent
import json
import uuid
import traceback

# 初始化调度代理
scheduler = SchedulerAgent()

# 对话历史管理
conversation_history = []
MAX_HISTORY = 5

# 同步包装器，用于在Gradio中调用异步函数
def sync_handle_request(user_input):
    """
    同步调用调度代理处理用户请求
    :param user_input: 用户输入的指令
    :return: 模型返回的响应
    """
    return asyncio.run(scheduler.handle_request(user_input))

def sync_complex_task(user_input):
    """
    同步调用复杂任务处理
    :param user_input: 用户输入的复杂任务描述
    :return: 任务处理结果
    """
    return asyncio.run(scheduler.complex_task(user_input))

# 主界面函数
def main_interface(user_input, chat_history, history_store, session_id):
    """
    处理用户输入并更新对话历史
    :param user_input: 用户输入的指令
    :param chat_history: 当前对话历史
    :param history_store: 历史对话存储
    :param session_id: 当前会话ID
    :return: 更新后的输入框、对话历史、历史存储、会话ID
    """
    if not user_input.strip():
        return "", chat_history, history_store, session_id

    # 调用模型获取响应
    try:
        bot_response = sync_handle_request(user_input)
    except Exception as e:
        bot_response = f"处理请求时出错：{str(e)}\n{traceback.format_exc()}"

    # 更新对话历史
    new_history = chat_history + [(user_input, bot_response)]

    return "", new_history, history_store, session_id

def create_new_chat(chat_history, history_store, session_id):
    """
    创建新对话并保存当前对话到历史
    :param chat_history: 当前对话历史
    :param history_store: 历史对话存储
    :param session_id: 当前会话ID
    :return: 新对话历史、更新后的历史存储、新会话ID
    """
    new_session_id = str(uuid.uuid4())[:8]

    # 保存当前对话到历史
    if chat_history:
        if len(history_store) >= MAX_HISTORY:
            history_store.pop(0)

        # 只取前几条记录作为预览
        preview = chat_history[0][0]
        if len(preview) > 50:
            preview = preview[:47] + "..."

        history_store.append({
            "session_id": session_id,
            "preview": preview,
            "full_conversation": chat_history.copy()
        })

    return [], history_store, new_session_id

def load_history(selected_index, history_store):
    """
    加载选中的历史对话
    :param selected_index: 选中的索引
    :param history_store: 历史对话存储
    :return: 加载的对话历史
    """
    if 0 <= selected_index < len(history_store):
        session = history_store[selected_index]
        return session["full_conversation"]
    return []

def clear_current_chat():
    """
    清除当前对话
    :return: 空对话历史
    """
    return []

def clear_all_history():
    """
    清除所有历史记录
    :return: 空历史存储
    """
    return []

def format_history_store(history_store):
    """
    格式化历史记录用于展示
    :param history_store: 历史对话存储
    :return: 格式化后的历史记录
    """
    return [
        [item["session_id"], item["preview"]]
        for item in history_store
    ]

# 创建Gradio界面
with gr.Blocks(title="Ploughman AI", theme=gr.themes.Default()) as demo:
    # 状态变量
    current_conversation = gr.State([])  # 当前对话历史
    history_store = gr.State([])         # 历史对话存储
    current_session_id = gr.State(str(uuid.uuid4())[:8])  # 当前会话ID

    # 界面标题
    gr.Markdown("# 🚜 Ploughman AI v1.0.0")
    gr.Markdown("### 智能数据分析与可视化助手")

    with gr.Row():
        with gr.Column(scale=2):
            # 数据库连接配置
            with gr.Accordion("🔌 数据库连接配置", open=False):
                with gr.Row():
                    db_host = gr.Textbox(label="数据库地址", value="192.168.2.60")
                    db_port = gr.Number(label="端口", value=3306)
                with gr.Row():
                    db_user = gr.Textbox(label="用户名", value="test")
                    db_password = gr.Textbox(label="密码", type="password", value="123456")
                with gr.Row():
                    db_name = gr.Dropdown(label="选择数据库", choices=["test_database", "information_schema"])
                    connect_btn = gr.Button("连接数据库", variant="primary")

            # 数据导入
            with gr.Accordion("📤 数据导入", open=False):
                excel_file = gr.File(label="上传数据文件", type="filepath")
                import_btn = gr.Button("导入数据", variant="primary")
                import_result = gr.JSON(label="导入结果")

            # 历史对话记录
            with gr.Accordion("📝 对话历史 (最多5条)", open=False):
                history_display = gr.Dataframe(
                    headers=["会话ID", "对话预览"],
                    datatype=["str", "str"],
                    interactive=True,
                    col_count=(2, "fixed"),
                    type="array"
                )
                delete_history_btn = gr.Button("删除选中记录", variant="secondary")

            # 对话控制按钮
            with gr.Row():
                new_chat_btn = gr.Button("新对话", variant="secondary")
                clear_history_btn = gr.Button("清除历史", variant="secondary")

        with gr.Column(scale=3):
            # 聊天界面
            chatbot = gr.Chatbot(
                label="Ploughman AI",
                height=500,
                bubble_full_width=False
            )
            msg = gr.Textbox(
                label="输入您的请求",
                placeholder="例如：分析...数据...、创建...图表...",
                lines=2
            )
            gr.Examples(
                examples=[
                    "分析人工智能领域的最新发展趋势",
                    "从数据库test_database中提取employees表的数据",
                    "根据生辰八字分析'张三'的财运（出生日期1990-05-12）",
                    "获取'李四'的预计下班时间",
                    "将sales_data表的数据可视化为柱状图"
                ],
                inputs=[msg],
                label="示例请求"
            )
            with gr.Row():
                submit_btn = gr.Button("发送", variant="primary")
                clear_btn = gr.Button("清除对话", variant="secondary")

            # 查询结果展示
            with gr.Accordion("📊 查询结果与可视化", open=False):
                query_result = gr.JSON(label="数据结果")
                result_visualization = gr.Image(label="可视化结果", interactive=False)

    # 事件处理函数
    submit_btn.click(
        fn=main_interface,
        inputs=[msg, current_conversation, history_store, current_session_id],
        outputs=[msg, current_conversation, history_store, current_session_id]
    )

    clear_btn.click(
        fn=clear_current_chat,
        inputs=[],
        outputs=[current_conversation]
    )

    new_chat_btn.click(
        fn=create_new_chat,
        inputs=[current_conversation, history_store, current_session_id],
        outputs=[current_conversation, history_store, current_session_id]
    )

    clear_history_btn.click(
        fn=clear_all_history,
        inputs=[],
        outputs=[history_store]
    )

    delete_history_btn.click(
        fn=lambda idx, hs: (hs[:idx] + hs[idx+1:], []) if 0 <= idx < len(hs) else (hs, []),
        inputs=[history_display, history_store],
        outputs=[history_store, history_display]
    )

    # 当历史记录更新时重新格式化显示
    history_store.change(
        fn=format_history_store,
        inputs=[history_store],
        outputs=[history_display]
    )

    # 当前对话显示
    current_conversation.change(
        fn=lambda x: x,
        inputs=[current_conversation],
        outputs=[chatbot]
    )

    # 绑定历史记录选择事件
    history_display.select(
        fn=lambda idx, hs: hs[idx]["full_conversation"] if 0 <= idx < len(hs) else [],
        inputs=[history_display, history_store],
        outputs=[current_conversation]
    )

    # 数据导入事件
    import_btn.click(
        fn=lambda file_path: json.dumps({"file_path": file_path, "status": "ready"}),
        inputs=[excel_file],
        outputs=[import_result]
    )

if __name__ == "__main__":
    # 启动Gradio界面
    demo.queue()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )