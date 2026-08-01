import sqlite3
import streamlit as st

from database import init_db, add_note_with_tags, update_note, delete_note


DB_NAME = "knowledge.db"


def _get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_notes_with_tags_and_time():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT n.id, n.title, n.content, n.created_time, GROUP_CONCAT(t.name)
        FROM notes n
        LEFT JOIN note_tags nt ON nt.note_id = n.id
        LEFT JOIN tags t ON t.id = nt.tag_id
        GROUP BY n.id
        ORDER BY n.id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()

    notes = []
    for row in rows:
        note_id, title, content, created_time, tag_string = row
        tags = tag_string.split(",") if tag_string else []
        notes.append((note_id, title, content, created_time, tags))

    return notes


# 初始化数据库
init_db()


st.title("🧠 我的 AI 个人知识库")

st.markdown(
    """
    <style>
        .note-card {
            border: 1px solid #e6e6e6;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 18px;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
        }
        .note-card-header {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            align-items: flex-start;
        }
        .note-title {
            margin: 0;
            color: #111827;
            font-size: 1.25rem;
            font-weight: 600;
        }
        .note-meta {
            color: #6b7280;
            font-size: 0.95rem;
            margin: 0;
        }
        .note-tags {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .note-tag {
            display: inline-block;
            background: #eef2ff;
            color: #3730a3;
            border-radius: 9999px;
            padding: 4px 10px;
            font-size: 0.85rem;
        }
        .stButton>button,
        .stButton button,
        button[data-testid="stButton"] {
            border-radius: 9999px;
            border: 1px solid rgba(15, 23, 42, 0.12);
            background-color: #f8fafc;
            color: #111827;
            box-shadow: none !important;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 38px;
            transition: background-color 0.15s ease, transform 0.1s ease;
        }
        .stButton>button:hover,
        .stButton button:hover,
        button[data-testid="stButton"]:hover {
            background-color: #eef2ff;
        }
        .stButton>button:active,
        .stButton button:active,
        button[data-testid="stButton"]:active {
            background-color: #e2e8f0;
            transform: translateY(1px);
        }
    </style>
    """,
    unsafe_allow_html=True
)


title = st.text_input(
    "笔记标题"
)


content = st.text_area(
    "笔记内容（支持 Markdown）",
    help="请输入 Markdown 内容，保存后会以原文保存"
)

tags = st.text_input(
    "标签",
    help="多个标签请用逗号分隔，可用于后续标签功能扩展"
)

st.subheader("📖 Markdown 实时预览")

if content:

    st.markdown(content)

else:

    st.info("请输入 Markdown 内容后，可在此看到预览")


if st.button("保存笔记"):

    if title and content:

        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        add_note_with_tags(title, content, tag_list)

        st.success("保存成功！")

    else:

        st.warning("请输入标题和内容")



st.divider()


tags_filter = st.selectbox(
    "标签筛选",
    options=["全部", "Python", "AI", "Vibe Coding"],
    index=0,
    help="选择标签查看对应笔记，默认为全部"
)

search_keyword = st.text_input(
    "搜索关键词",
    help="输入标题或内容中的关键词进行搜索"
)


notes = get_notes_with_tags_and_time()

if tags_filter != "全部":
    notes = [note for note in notes if tags_filter in note[4]]

if search_keyword:
    keyword = search_keyword.lower()
    notes = [
        note for note in notes
        if keyword in note[1].lower() or keyword in note[2].lower()
    ]

result_count = len(notes)
summary_parts = []
if tags_filter != "全部":
    summary_parts.append(f"标签：{tags_filter}")
if search_keyword:
    summary_parts.append(f"关键词：{search_keyword}")
summary_text = "，".join(summary_parts) if summary_parts else "显示全部笔记"

if result_count == 0:
    st.info(f"未找到匹配的笔记。当前筛选条件：{summary_text}。请调整标签或关键词后重试。")
else:
    st.caption(f"共 {result_count} 条笔记符合条件，{summary_text}。")

st.subheader("📚 我的历史笔记")

for note in notes:
    note_id, title, content, created_time, note_tags = note
    container = st.container()
    with container:
        st.markdown(
            f"""
            <div class='note-card'>
              <div class='note-card-header'>
                <div>
                  <h3 class='note-title'>{title}</h3>
                  <p class='note-meta'>创建时间：{created_time}</p>
                </div>
              </div>
            """,
            unsafe_allow_html=True
        )
        if note_tags:
            st.markdown(
                "<div class='note-tags'>" + "".join([f"<span class='note-tag'>{tag}</span>" for tag in note_tags]) + "</div>",
                unsafe_allow_html=True
            )

        action_cols = st.columns([1, 1])
        with action_cols[0]:
            if st.button("编辑", key=f"edit-{note_id}"):
                st.session_state["editing_note_id"] = note_id
                st.session_state["editing_title"] = title
                st.session_state["editing_content"] = content
        with action_cols[1]:
            if st.button("删除", key=f"delete-{note_id}"):
                delete_note(note_id)
                st.success("已删除该笔记")
                st.rerun()

        if st.session_state.get("editing_note_id") == note_id:
            edit_title = st.text_input(
                "编辑标题",
                value=st.session_state.get("editing_title", title),
                key=f"edit-title-{note_id}"
            )
            edit_content = st.text_area(
                "编辑内容（支持 Markdown）",
                value=st.session_state.get("editing_content", content),
                key=f"edit-content-{note_id}"
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("保存修改", key=f"save-{note_id}"):
                    if edit_title and edit_content:
                        update_note(note_id, edit_title, edit_content)
                        for key in ["editing_note_id", "editing_title", "editing_content"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.success("笔记已更新")
                        st.rerun()
                    else:
                        st.warning("标题和内容不能为空")
            with btn_col2:
                if st.button("取消", key=f"cancel-{note_id}"):
                    for key in ["editing_note_id", "editing_title", "editing_content"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        else:
            with st.expander("展开正文", expanded=False):
                st.markdown(content)

        st.markdown("</div>", unsafe_allow_html=True)
