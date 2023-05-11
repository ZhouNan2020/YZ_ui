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

    def uploader(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"])

    def explain(self):
        if self.file is not None:
            st.sidebar.write(self.file.name)
        # return self.file


# 实例化并调用
file_uploader = FileUploader()
file_uploader.uploader()
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


class DataPrepare(FileUploader):
    # 在__init__中定义这个类将直接使用FileUploader中被上传的文件，将文件赋值给self.data供后面的函数调用
    def __init__(self):
        super().__init__()
        # 我需要self的数据类型不是None，而是dataframe，所以我在这里定义了一个self.data，这个dataframe将在之后的函数中被赋值
        self.data = pd.read_excel(self.file, sheet_name=None, header=0)
        self.data = pd.concat(self.data, ignore_index=True)
        # 将self.data中的所有列名赋值给self.data_columns
        self.data_columns = self.data.columns





class CaseSeriesStudy(DataPrepare):
    def __init__(self):
        super().__init__()
        self.outcome = None
        self.exposure_factor = None
        self.case_series_sub_group = None
        self.research_var = None

    '''病例系列研究：
    选项一：“选择研究的目标变量及组别”，分为两个selectbox，
            第1个是“选择研究的目标变量”，选项是self.data_columns中的变量名，结果赋值给research_VAR,
            第2个是“选择研究的组别”，选项是self.data中research_VAR这一列的不同值，结果赋值给case_series_sub_group.
    选项二: "选择暴露因素",选项是self.data_columns中的变量名，结果赋值给exposure_factor
    选项三：“选择结局指标”，选项是self.data_columns中的变量名，结果赋值给outcome
    全部选择结束之后，self.data将保留research_VAR中的值为case_series_sub_group的行，并根据exposure_factor分为不同的组，
    根据组的数量，在一个selectbox中使用“第X组”选择查看不同组的st.dataframe,其中X为INT类型的数字，从1开始，最大值为组的数量。
    用@cache缓存函数的返回值，避免st频繁刷新'''

    @st.cache
    def case_series_study_1(self):
        self.research_var = st.selectbox("选择研究的目标变量及组别", self.data_columns)
        self.case_series_sub_group = st.selectbox("选择研究的组别", self.data[self.research_var].unique().tolist())

    @st.cache
    def case_series_study_2(self):
        self.exposure_factor = st.selectbox("选择暴露因素", self.data_columns)
        self.outcome = st.selectbox("选择结局指标", self.data_columns)

    def case_series_study_3(self):
        self.data = self.data[self.data[self.research_var] == self.case_series_sub_group]
        self.data = self.data.groupby(self.exposure_factor).mean()
        self.data.reset_index(inplace=True)
        self.data["组别"] = self.data[self.exposure_factor].apply(
            lambda x: "第{}组".format(self.data[self.exposure_factor].tolist().index(x) + 1))
        self.data = self.data.loc[:, ["组别", self.outcome]]
        self.data.rename(columns={self.outcome: "结局指标"}, inplace=True)
        group_number = st.selectbox("选择查看的组别", self.data["组别"].tolist())
        self.data = self.data[self.data["组别"] == group_number]
        st.dataframe(self.data)
        return self.data


class CrossSectionalStudy(DataPrepare):
    def __init__(self):
        super().__init__()
        self.ob_radio_var = None
        self.inclu_var = None

    '''横断面研究：
    选项一：“选择患病率观察指标”，选项是self.data_columns中的变量名，结果赋值给ob_radio_var,
    选项二：“选择将纳入分析的变量”，选项是self.data_columns中的变量名，结果赋值给inclu_var,这个使用多选框。
    需要对ob_radio_var进行预处理，使用单选框选择ob_radio_var是分类变量还是连续变量。
    使用st.radio判定ob_radio_var是“分类变量”还是“连续变量”
    如果ob_radio_var是分类变量，提供输入框选择哪个数字代表患病
    如果ob_radio_var是连续变量，提供输入框选择患病率的判定方式，大于还是小于，以及判定的阈值.
    然后使用1表示“患病”，0表示“未患病”，替换self.data中ob_radio_var的值，列名为“incidence”，
    最后将incidence与inclu_var合并，使用st.dataframe展示结果。'''

    def cross_sectional_study(self):
        ob_radio_var = st.selectbox("选择患病率观察指标", self.data_columns)
        inclu_var = st.multiselect("选择将纳入分析的变量", self.data_columns)
        ob_radio_var_type = st.radio("选择患病率观察指标的类型", ["分类变量", "连续变量"])
        if ob_radio_var_type == "分类变量":
            ob_radio_var_value = st.text_input("输入哪个值代表患病", 1)
            # 将self.data中表示患病的值替换为1，其它值均替换为0
            self.data[ob_radio_var] = self.data[ob_radio_var].apply(lambda x: 1 if x == ob_radio_var_value else 0)
        else:
            ob_radio_var_value = st.selectbox("输入患病率的判定方式", [">", "<", "=", ">=", "<=", "!="],
                                              key="ob_radio_var_value")
            ob_radio_var_value2 = st.text_input("输入患病率的阈值", 0.5)
            # 将符合eval（ob_radio_var_value和ob_radio_var_value2）的值替换为1，其它值均替换为0。注意：目前获取的值为str，需要转换为可供计算与比较的形式
            self.data[ob_radio_var] = self.data[ob_radio_var].apply(
                lambda x: 1 if eval(str(x) + ob_radio_var_value + ob_radio_var_value2) else 0)
        self.data.rename(columns={ob_radio_var: "incidence"}, inplace=True)
        self.data = self.data[inclu_var + ["incidence"]]
        st.dataframe(self.data)


class StudyTypeSelector(CaseSeriesStudy, CrossSectionalStudy):
    def __init__(self):
        super().__init__()
        self.study_type = None


    def select_study_type(self):
        self.study_type = st.selectbox("选择研究类型", ["病例系列研究", "横断面研究"])
        return self.study_type


# 定义一个类CallGenerator，继承StudyTypeSelector类，用于调用研究类型，要首先判定FileUploader是否已经接受到上传的文件，如果为空，提示用户上传文件，如果不为空，调用select_study_type方法，判定研究类型，如果是病例系列研究，调用case_series_study方法，如果是横断面研究，调用cross_sectional_study方法。
class CallGenerator(StudyTypeSelector):
    # 将FileUploader接受到的文件赋值给self.used_file
    def __init__(self):
        super().__init__()
        self.used_file = file_uploader.file

    def call(self):
        if self.used_file is None:
            st.warning("请上传文件")
        else:
            study_type = self.select_study_type()
            if study_type == "病例系列研究":
                self.case_series_study_3()
            else:
                self.cross_sectional_study()



# 实例化并调用
with tab2:
    call = CallGenerator()
    call.call()



