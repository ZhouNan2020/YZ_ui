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

    def __init__(self, file):
        self.file = file
        data = pd.read_excel(self.file, sheet_name=None, header=0)
        data = pd.concat(data, ignore_index=True)
        data = data.infer_objects()
        self.data = pd.DataFrame(data)
        self.data_columns = self.data.columns
        self.data_columns = self.data_columns.tolist()

    '''定义一个函数，用于从self.data_columns中选择需要纳入描述性统计的列，使用st.multiselect，将选择的列赋值给self.selected_columns，然后使用被选中的列名从self.data中提取数据，使用st.dataframe显示'''
    @st.cache
    def descriptive_select_columns(self):
        st.write("选择需要纳入描述性统计的列")
        selected_columns = st.multiselect("选择需要纳入描述性统计的列", self.data_columns)
        return selected_columns

    def descriptive_read_columns(self):
        # 调用descriptive_select_columns的返回值，从self.data中提取数据，赋值给selected_data
        selected_data = self.data[self.descriptive_select_columns()]
        return selected_data



class DescriptiveStatistics(DataPrepare):
    def __init__(self,file):
        super().__init__(file)

    @st.experimental_singleton
    def descriptive_statistics(_self):
        # 给一个button，用于触发描述性统计的计算
        if st.button("开始分析"):
            # 调用descriptive_select_columns函数，将返回值赋值给selected_data和selected_columns
            selected_data, selected_columns = _self.descriptive_select_columns()
            if selected_columns is None:
                st.write("请选择需要纳入描述性统计的列")
            else:
                # 获取descriptive_read_columns的返回值，进行描述性统计
                selected_data = _self.descriptive_read_columns()
                # 使用st.dataframe显示描述性统计的结果
                st.dataframe(selected_data.describe())






















# 定义一个类CallGenerator，继承StudyTypeSelector类，用于调用研究类型，要首先判定FileUploader是否已经接受到上传的文件，如果为空，提示用户上传文件，如果不为空，调用select_study_type方法，判定研究类型，如果是病例系列研究，调用case_series_study方法，如果是横断面研究，调用cross_sectional_study方法。
def study_type():
    study_type = st.selectbox("选择研究类型", ["未选择","描述性统计", "横断面研究"])
    return study_type


class Generator(DescriptiveStatistics):
    def __init__(self,file):
        super().__init__(file)

    # 将FileUploader接受到的文件赋值给self.used_file

    def gener(self):
        study = study_type()
        if study == "描述性统计":
            self.descriptive_statistics()
        else:
            pass


def call():
    if file_uploader.file is None:
        st.warning("请上传文件")
    else:
        gen = Generator(file_uploader.file)
        gen.gener()

# 实例化并调用
with tab2:

    call()
