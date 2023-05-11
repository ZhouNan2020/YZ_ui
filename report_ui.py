# import streamlit和其它的处理word的库
import os

import streamlit as st

# ______________________________________
# 在整个脚本中，能够使用@cache缓存的函数一定要用@st.cache
# 用于缓存函数的返回值，避免st频繁刷新
# 项目标题“优卓医药科技”

st.set_page_config(page_title="优卓医药科技", page_icon="🧊", layout="wide")

# 定义一个class，在st.sidebar中中用于上传excel，在上传之后，在sidebar中显示上传的文件名，并且显示excel中的sheet名
class FileUploader:
    def __init__(self):
        self.file = None
        self.sheet = None
        self.sheet_names = None

    def upload(self):
        self.file = st.sidebar.file_uploader(
            label="上传excel文件",
            type=["xlsx", "xls"],
            accept_multiple_files=False,
            key="file_uploader",
        )
        if self.file:
            self.sheet_names = self.get_sheet_names()
            self.sheet = st.sidebar.selectbox(
                label="选择sheet", options=self.sheet_names, key="sheet"
            )
        return self.file, self.sheet

    def get_sheet_names(self):
        import pandas as pd

        df = pd.ExcelFile(self.file)
        return df.sheet_names

# 实例化并调用
file_uploader = FileUploader()
file, sheet = file_uploader.upload()
