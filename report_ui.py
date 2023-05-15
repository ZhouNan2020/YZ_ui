# import streamlit和其它的处理word的库
import docx
import pandas as pd
import streamlit as st
# 导入import docx和Python-docx-template

from docxtpl import DocxTemplate
from streamlit import session_state
from streamlit.runtime.state import SessionState
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

# ______________________________________
# 在整个脚本中，能够使用@cache缓存的函数一定要用@st.cache
# 用于缓存函数的返回值，避免st频繁刷新
# 项目标题“优卓医药科技”

st.set_page_config(page_title="优卓医药科技", page_icon="🧊", layout="wide")
# 将主界面分一下st.tab，分成3个tab，分别是“数据浏览”，“报告生成”，“关于”
tab1, tab2, tab3, tab4 = st.tabs(["数据浏览", "数据预处理","报告生成", "关于"])


# 定义一个class，在st.sidebar中中用于上传excel，并显示文件名
class FileUploader:
    def __init__(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"], key="file_uploader")

    # def uploader(self):
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
        self.selected_data = None
        self.selected_columns = None
        self.file = file
        data = pd.read_excel(self.file, sheet_name=None, header=0)
        data = pd.concat(data, ignore_index=True)
        data = data.infer_objects()
        self.data = pd.DataFrame(data)
        self.data_columns = self.data.columns
        self.data_columns = self.data_columns.tolist()




class DataPreprocessing(DataPrepare):
        def __init__(self, file):
            super().__init__(file)
            self.selected_cols = []
            self.transformed_cols = []

        def encode_categorical(self, col):
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            self.transformed_cols.append(col)

        def fill_missing(self, col, method):
            if method == 'mode':
                self.data[col].fillna(self.data[col].mode()[0], inplace=True)
            elif method == 'mean':
                self.data[col].fillna(self.data[col].mean(), inplace=True)
            elif method == 'median':
                self.data[col].fillna(self.data[col].median(), inplace=True)
            self.transformed_cols.append(col)

        def create_dummies(self, col):
            dummies = pd.get_dummies(self.data[col], prefix=col)
            self.data = pd.concat([self.data, dummies], axis=1)
            self.transformed_cols.append(col)

        def standardize(self):
            scaler = StandardScaler()
            self.data = scaler.fit_transform(self.data)
            self.transformed_cols = self.columns

        def show_sidebar(self):
            self.selected_cols = st.sidebar.multiselect('Select columns to preprocess', self.columns)
            st.sidebar.write('Selected columns:', self.selected_cols)
            if st.sidebar.checkbox('Encode categorical variables'):
                cat_cols = [col for col in self.selected_cols if self.data[col].dtype == 'object']
                for col in cat_cols:
                    self.encode_categorical(col)
            if st.sidebar.checkbox('Fill missing values'):
                for col in self.selected_cols:
                    if self.data[col].isnull().sum() > 0:
                        if self.data[col].dtype == 'object':
                            method = 'mode'
                        elif abs(self.data[col].skew()) <= 1:
                            method = 'mean'
                        else:
                            method = 'median'
                        self.fill_missing(col, method)
            if st.sidebar.checkbox('Create dummy variables'):
                cat_cols = [col for col in self.selected_cols if self.data[col].dtype == 'object']
                for col in cat_cols:
                    self.create_dummies(col)
            if st.sidebar.checkbox('Standardize data'):
                self.standardize()

        def show_transformed_data(self):
            st.write('Transformed data:')
            st.write(self.data[self.transformed_cols])




with tab2:
    data_preprocessing = DataPreprocessing(file_uploader.file)
    data_preprocessing.show_sidebar()
    data_preprocessing.show_transformed_data()



















class DescriptiveStatistics(DataPrepare):
    def __init__(self, file):
        super().__init__(file)
        self.all_columns = self.data.columns.tolist()

    @st.cache
    def get_selected_columns(self, selected_columns):
        return self.data[selected_columns]
    def descriptive_select_columns(self, selected_columns):
        st.dataframe(self.get_selected_columns(session_state.Descriptive_multiselect_1))


# class DescriptiveStatistics(DescriptiveStatisticsOfData):
#    def __init__(self, file):
#        super().__init__(file)
#
#    def descriptive_statistics(self):
#        # 给一个button，用于触发描述性统计的计算
#        # 调用descriptive_select_columns函数，将返回值赋值给selected_data和selected_columns
#        super().descriptive_select_columns()
#        # 使用st.write显示selected_data
#        st.write(self.selected_data)


# 定义一个类CallGenerator，继承StudyTypeSelector类，用于调用研究类型，要首先判定FileUploader是否已经接受到上传的文件，如果为空，提示用户上传文件，如果不为空，调用select_study_type方法，判定研究类型，如果是病例系列研究，调用case_series_study方法，如果是横断面研究，调用cross_sectional_study方法。
def study_type():
    study_type = st.selectbox("选择研究类型", ["未选择", "描述性统计", "横断面研究"])
    return study_type


class Generator(DescriptiveStatistics):
    def __init__(self, file):
        super().__init__(file)
        # 使用session_state记录用户选择的列(get不能用）

    # 将FileUploader接受到的文件赋值给self.used_file

    def gener(self):
        study = study_type()
        if study == "描述性统计":
            st.title("数据探索")
            st.write("请选择要展示的列：")
            selected_columns = st.multiselect("选择列", self.all_columns, key="Descriptive_multiselect_1")

            if st.button("生成"):
                self.descriptive_select_columns(selected_columns)
        else:
            pass


def call():
    if file_uploader.file is None:
        st.warning("请上传文件")
    else:
        gen = Generator(file_uploader.file)
        gen.gener()


# 实例化并调用
with tab3:
    call()

with tab4:
    # 使用@cache定义一个st.session_state的函数示例，初始为0，让用户点击，每点击一次计数+1,但是不要实时显示更改，要在点击submit后，才将总的点击次数显示出来,合并@cache使用，避免st频繁刷新
    if "count" not in st.session_state:
        st.session_state.count = 0
    st.write("点击次数：", st.session_state.count)
    if st.button("点击"):
        st.session_state.count += 1
    if st.button("submit"):
        st.write("点击次数：", st.session_state.count)


        

