# import streamlit和其它的处理word的库
import os

import streamlit as st

# ______________________________________
# 在整个脚本中，能够使用@cache缓存的函数一定要用@st.cache
# 用于缓存函数的返回值，避免st频繁刷新
# 项目标题“优卓医药科技”

st.set_page_config(page_title="优卓医药科技", page_icon="🧊", layout="wide")
# 将主界面分一下st.tab，分成3个tab，分别是“数据浏览”，“报告生成”，“关于”
tab1, tab2, tab3 = st.tabs(["数据浏览", "报告生成", "关于"])


# 定义一个class，在st.sidebar中中用于上传excel，并显示文件名
class FileUploader:
    def __init__(self):
        self.file = None

    def run(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"])
        if self.file is not None:
            st.sidebar.write(self.file.name)
        return self.file

# 实例化并调用
file_uploader = FileUploader()
file_uploader.run()

