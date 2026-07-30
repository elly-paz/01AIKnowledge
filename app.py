import streamlit as st

from database import init_db, add_note, get_notes


# 初始化数据库
init_db()


st.title("🧠 我的 AI 个人知识库")


title = st.text_input(
    "笔记标题"
)


content = st.text_area(
    "笔记内容"
)


if st.button("保存笔记"):

    if title and content:

        add_note(title, content)

        st.success("保存成功！")

    else:

        st.warning("请输入标题和内容")



st.divider()


st.subheader("📚 我的历史笔记")


notes = get_notes()


for note in notes:

    st.markdown(
        f"""
        ### {note[0]}

        {note[1]}
        """
    )