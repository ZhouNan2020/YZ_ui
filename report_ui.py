# import streamlit和其它的处理word的库
import os

import streamlit as st

# ______________________________________
# 在整个脚本中，能够使用@cache缓存的函数一定要用@st.cache
# 用于缓存函数的返回值，避免st频繁刷新
# 项目标题“优卓医药科技”

st.set_page_config(page_title="优卓医药科技", page_icon="🧊", layout="wide")

# 定义一个class，在侧栏用于上传和展示目前的文件名称，会上传一个excel，展示这个excel的文件名和每一个sheet的名称，使sheet名称可被选中
class FileSelector(object):
def __init__(self, label="Upload"):
        self.label = label

    def file_selector(self, folder_path="./"):
        filenames = os.listdir(folder_path)
        selected_filename = st.selectbox(self.label, filenames)
        return os.path.join(folder_path, selected_filename)


