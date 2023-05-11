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
        self.file = None

    def run(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"])
        if self.file is not None:
            st.sidebar.write(self.file.name)
        # return self.file


# 实例化并调用
file_uploader = FileUploader()
file_uploader.run()

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


class ReportGenerator(FileUploader):
    # 在__init__中定义这个类将直接使用FileUploader中被上传的文件，将文件赋值给self.file供后面的函数调用，同时定义一个self函数在不同的功能中调用根目录中不同的word模板
    def __init__(self):
        super().__init__()

        self.report_type = None
        self.template = None

    # 定义tab2界面顶端的选择栏，使用st.selectbox，名称是“选择研究类型”，选项是“病例系列研究“，”横断面研究“，”回顾型队列研究“，选项的不同结果赋值给self.report_type
    def select_report_type(self):
        self.report_type = st.selectbox("选择研究类型", ["病例系列研究", "横断面研究", "回顾型队列研究"])
        return self.report_type

    # 首先判定是否已经上传文件，如果未上传文件，提示用户上传文件，如果已经上传文件，调用read_data函数读取文件中的数据
    # 使用一个函数读取FileUploader类中所上传excel1的全部sheet中的数据，将其合并成为一个dataframe，index的名称是'subject_id',除index之外，如果有相同的变量名，则只保留一个
    # 合并完成后，读取这个dataframe的列名，这个值将会在之后的函数中作为备选变量
    # 赋值给self.data
    def read_data(self):
        if self.file is None:
            st.write("请上传文件")
        else:
            self.data = pd.read_excel(self.file, sheet_name=None, header=0)
            self.data = pd.concat(self.data.values(), ignore_index=True)
            self.data = self.data.loc[:, ~self.data.columns.duplicated()]
            self.data_columns = self.data.columns
            return self.data

    '''当用户选择病例系列研究时，从根目录中选择 self.template为case_series_study.docx
    选项一：“选择研究的目标变量及组别”，分为两个selectbox，
            第1个是“选择研究的目标变量”，选项是self.data_columns中的变量名，结果赋值给research_VAR,
            第2个是“选择研究的组别”，选项是self.data中research_VAR这一列的不同值，结果赋值给case_series_sub_group.
    选项二: "选择暴露因素",选项是self.data_columns中的变量名，结果赋值给exposure_factor
    选项三：“选择结局指标”，选项是self.data_columns中的变量名，结果赋值给outcome
    全部选择结束之后，self.data将保留research_VAR中的值为case_series_sub_group的行，并根据exposure_factor分为不同的组，
    根据组的数量，在一个selectbox中使用“第X组”选择查看不同组的st.dataframe,其中X为INT类型的数字，从1开始，最大值为组的数量。
    用@cache缓存函数的返回值，避免st频繁刷新'''

    def case_series_study(self):
        self.template = "case_series_study.docx"
        research_var = st.selectbox("选择研究的目标变量及组别", self.data_columns)
        case_series_sub_group = st.selectbox("选择研究的组别", self.data[research_var].unique().tolist())
        exposure_factor = st.selectbox("选择暴露因素", self.data_columns)
        outcome = st.selectbox("选择结局指标", self.data_columns)
        self.data = self.data[self.data[research_var] == case_series_sub_group]
        self.data = self.data.groupby(exposure_factor).mean()
        self.data.reset_index(inplace=True)
        self.data["组别"] = self.data[exposure_factor].apply(
            lambda x: "第{}组".format(self.data[exposure_factor].tolist().index(x) + 1))
        self.data = self.data.loc[:, ["组别", outcome]]
        self.data.rename(columns={outcome: "结局指标"}, inplace=True)
        group_number = st.selectbox("选择查看的组别", self.data["组别"].tolist())
        self.data = self.data[self.data["组别"] == group_number]
        st.dataframe(self.data)
        return self.data


# 实例化并调用
with tab2:
    report_generator = ReportGenerator()
    report_generator.select_report_type()
    report_generator.read_data()
    if report_generator.report_type == "病例系列研究":
        report_generator.case_series_study()

