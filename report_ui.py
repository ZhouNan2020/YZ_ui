# import streamlit和其它的处理word的库
import os

import streamlit as st

# ______________________________________
# 在整个脚本中，能够使用@cache缓存的函数一定要用@st.cache
# 用于缓存函数的返回值，避免st频繁刷新
# 项目标题“优卓医药科技”

st.set_page_config(page_title="优卓医药科技", page_icon="🧊", layout="wide")

# 定义一个class，在侧栏用于上传excel数据文件，并且要展示这个excel的文件名和每一个sheet的名称，使sheet名称可被选中。注意使用@st.cache
# 用于上传excel文件的类
class UploadFile:
    def __init__(self):
        self.file = None
        self.sheet = None
        self.sheet_name = None

    def upload(self):
        self.file = st.file_uploader("上传文件", type=["xlsx", "xls"])
        if self.file is not None:
            self.sheet_name = [i for i in self.file.sheet_names]
            self.sheet = st.selectbox("选择工作表", self.sheet_name)
            return self.file, self.sheet

    def get_file(self):
        return self.file

    def get_sheet(self):
        return self.sheet

    def get_sheet_name(self):
        return self.sheet_name

# 实例化
upload_file = UploadFile()
