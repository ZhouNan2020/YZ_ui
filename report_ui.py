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
        # 构造函数继承DataPrepare并且超类调用
        def __init__(self, file):
            super().__init__(file)
            self.data_columns = self.data.columns.tolist()
            self.selected_data = None

        # 定义一个函数，功能是将一个被选中的self.data_selected_columns转换成数字编码格式
        @st.cache_data
        def label_encoder(self, selected_columns):
            label_encoder = LabelEncoder()
            self.data[selected_columns] = label_encoder.fit_transform(self.data[selected_columns])
            return self.data[selected_columns]

        # 定义一个函数，功能连续变量缺失值插补，如果偏度绝对值不大于1，使用均值填补。如果偏度绝对值大于1，使用中位数填补。
        @st.cache_data
        def continuous_variable_missing_value_imputation(self, selected_columns):
            skew = self.data[selected_columns].skew()
            if abs(skew) <= 1:
                self.data[selected_columns] = self.data[selected_columns].fillna(self.data[selected_columns].mean())
            else:
                self.data[selected_columns] = self.data[selected_columns].fillna(self.data[selected_columns].median())
            return self.data[selected_columns]

        # 定义一个函数，功能是分类变量缺失值插补，使用众数填补
        @st.cache_data
        def categorical_variable_missing_value_imputation(self, selected_columns):
            self.data[selected_columns] = self.data[selected_columns].fillna(self.data[selected_columns].mode()[0])
            return self.data[selected_columns]

        # 定义一个函数，功能是连续变量离散化，使用等频法
        @st.cache_data
        def continuous_variable_discretization(self, selected_columns):
            self.data[selected_columns] = pd.qcut(self.data[selected_columns], 10, labels=False)
            return self.data[selected_columns]

        # 定义一个函数，功能是连续变量标准化，使用标准差标准化
        @st.cache_data
        def continuous_variable_standardization(self, selected_columns):
            self.data[selected_columns] = (self.data[selected_columns] - self.data[selected_columns].mean()) / self.data[selected_columns].std()
            return self.data[selected_columns]

        # 定义一个函数，功能是连续变量归一化，使用最大最小值归一化
        @st.cache_data
        def continuous_variable_normalization(self, selected_columns):
            self.data[selected_columns] = (self.data[selected_columns] - self.data[selected_columns].min()) / (self.data[selected_columns].max() - self.data[selected_columns].min())
            return self.data[selected_columns]

        # 定义一个函数，功能是转换哑变量，并且将转换后的列放入原数据集中
        @st.cache_data
        def dummy_variable(self, selected_columns):
            dummy_data = pd.get_dummies(self.data[selected_columns], prefix=selected_columns)
            self.data = pd.concat([self.data, dummy_data], axis=1)
            return self.data


# 定义一个类，功能是展示出数据集中的所有列，每个列后跟一个checkbox，每一个checkbox对应DataPreprocessing类中的一个预处理方法，使用st.session_state保存用户选择的项，并在点击按钮后调用这些方法
class PreprocessingExecution(DataPreprocessing):
    def __init__(self, file):
        super().__init__(file)
        self.all_columns = self.data.columns.tolist()
    # streamlit的展示函数，使用st.write逐行显示所有列名，每个列名下面显示一个一个checkbox
    @st.cache_data
    def preprocessing_multiselect(self):
        for column in self.all_columns:
            st.write(column)
            st.checkbox("数字编码","连续变量缺失值插补","分类变量缺失值插补","连续变量离散化","连续变量标准化","连续变量归一化","转换哑变量")
    # 定义一个函数，功能是将用户选择的checkbox对应的方法调用
    @st.cache_data
    def preprocessing_execution(self):
        if self.file is not None:
            for column in self.all_columns:
                if st.checkbox("数字编码"):
                    self.label_encoder(column)
                if st.checkbox("连续变量缺失值插补"):
                    self.continuous_variable_missing_value_imputation(column)
                if st.checkbox("分类变量缺失值插补"):
                    self.categorical_variable_missing_value_imputation(column)
                if st.checkbox("连续变量离散化"):
                    self.continuous_variable_discretization(column)
                if st.checkbox("连续变量标准化"):
                    self.continuous_variable_standardization(column)
                if st.checkbox("连续变量归一化"):
                    self.continuous_variable_normalization(column)
                if st.checkbox("转换哑变量"):
                    self.dummy_variable(column)
        return self.data
    # 定义一个函数，功能是将预处理后的数据集返回










# with tab2:
#     # 调用
#     preprocessing = PreprocessingExecution(file_uploader.file)
#     preprocessing.preprocessing_multiselect()
#     if st.button("执行"):
#         preprocessing.preprocessing_execution()





















class DescriptiveStatistics(DataPrepare):
    def __init__(self, file):
        super().__init__(file)
        self.all_columns = self.data.columns.tolist()

    @st.cache
    def get_selected_columns(self, selected_columns):
        return self.data[selected_columns]
    def descriptive_select_columns(self,selected_columns):
        selected_data = self.get_selected_columns(selected_columns)
        st.dataframe(selected_data)
        return selected_data


    # 定义一个函数，功能是供用户选择要进行描述性统计的连续变量列，使用multiselect，并从原始数据集中选中提取这些列，并对选中列求出索引计数，mean±SD,中位数、最大值和最小值
    def DescriptiveStatisticsOfContinuousVariables(self,selected_columns):

        if selected_columns:
            selected_data=self.descriptive_select_columns(selected_columns)
            # 将selected_data转换为float类型
            selected_data = selected_data.astype(float)
            # 求出索引计数，mean±SD,中位数、最大值和最小值,不要使用describe
            # 求出本列的值计数，和nan值分开计数
            count = selected_data.count()
            nan_count = selected_data.isnull().sum()

            meanSD = selected_data.mean() + "±" + selected_data.std()

            median = selected_data.median()

            max = selected_data.max()

            min = selected_data.min()
            # 制作一个datafrmae，index分别为n (miss)，mean±SD,median、max和min,值分别为上面求出的值，其中n (miss)的值为count和nan_count合并在一个单元格内
            descriptive_statistics = pd.DataFrame({"n (miss)": count + "(" + nan_count + ")", "mean±SD": meanSD, "median": median, "max": max, "min": min})
            st.dataframe(descriptive_statistics)













        else:
            st.write("未选择列")





   


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

            selected_columns = st.multiselect("选择要进行描述性统计的连续变量列", self.all_columns)
            if st.button("生成"):
                self.descriptive_select_columns(selected_columns)
            # 定义一个button，点击后执行descriptive_statistics方法
            if st.button("连续变量描述性统计"):
                self.DescriptiveStatisticsOfContinuousVariables(selected_columns)
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


        

