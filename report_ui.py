# import streamlit和其它的处理word的库
import docx
import pandas as pd
import streamlit as st
# 导入import docx和Python-docx-template

from docxtpl import DocxTemplate

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
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"], key="file_uploader")

    #def uploader(self):
    #    self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"])

    def explain(self):
        if self.file is not None:
            st.sidebar.write(self.file.name)
        # return self.file


# 实例化并调用
file_uploader = FileUploader()

file_uploader.explain()
# ______________________________________
'''tab1的内容是展示数据，需要一个类，首先获取被上传excel文件中的所有sheet名称供选择，
将这些名称使用一个st.selectbox展示,在seclectbox中被选中的sheet将以st.dataframe显示'''


class SheetSelector:
    def __init__(self, file):
        self.file = file
        self.sheet_names = None
        self.selected_sheet = None

    def run(self):
        if self.file is not None:
            self.sheet_names = pd.ExcelFile(self.file).sheet_names
            self.selected_sheet = st.selectbox("选择一个sheet", self.sheet_names)
            # 用空白替换掉sheet中的NaN，赋值给exhibition_data
            exhibition_data = pd.read_excel(self.file, sheet_name=self.selected_sheet, header=0).fillna("")
            st.dataframe(exhibition_data)


# 实例化并调用
with tab1:
    sheet_selector = SheetSelector(file_uploader.file)
    sheet_selector.run()

# tab2
'''tab2的内容是生成报告，需要精细的处理一些word文档.首先需要定义一个大的类，这个类将用于选择user在这个模块中要做的工作，选项采用st.selectbox,
不同的选项将调用不同的功能和输入界面.这个类将继承上面的FileUploader类，因为在这个模块中需要上传excel文件.使用@cache缓存函数的返回值，避免st频繁刷新'''


class DataPrepare():
    # 在__init__中定义这个类将直接使用FileUploader中被上传的文件，将文件赋值给self.data供后面的函数调用

    def __init__(self,file):
        self.file = file
        data = pd.read_excel(self.file, sheet_name=None, header=0)
        data = pd.concat(data, ignore_index=True)
        data = data.infer_objects()
        self.data = pd.DataFrame(data)
        self.data_columns = self.data.columns
        self.data_columns = self.data_columns.tolist()

class DescriptiveStatistics(DataPrepare):
    def __init__(self,file):
        super().__init__(file)

    def descriptive_statistics(self):
        st.write("描述性统计")
        st.write(self.data.describe())











# 定义一个类CallGenerator，继承StudyTypeSelector类，用于调用研究类型，要首先判定FileUploader是否已经接受到上传的文件，如果为空，提示用户上传文件，如果不为空，调用select_study_type方法，判定研究类型，如果是病例系列研究，调用case_series_study方法，如果是横断面研究，调用cross_sectional_study方法。
def study_type():
    study_type = st.selectbox("选择研究类型", ["描述性统计", "横断面研究"])
    return study_type


class CallGenerator(DescriptiveStatistics):
    def __init__(self,file):
        super().__init__(file)

    # 将FileUploader接受到的文件赋值给self.used_file

    def call(self):
        if self.file is None:
            st.warning("请上传文件")
        else:
            study_type = study_type()
            if study_type == "病例系列研究":
                self.descriptive_statistics()
            else:
                pass


def call():
    if file_uploader.file is None:
        st.warning("请上传文件")
    else:
        call = CallGenerator(file_uploader.file)
        call.call()

# 实例化并调用
with tab2:

    call()
