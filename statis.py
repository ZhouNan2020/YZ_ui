#%%
#%%
import numpy as np
import pandas as pd
import streamlit as st


 
# 设置streamlit的网页标题为“优卓医药科技”
st.set_page_config(page_title="优卓医药科技")



# 分文两个tab，第一个tab名称为“分组”，第二个tab名称为“关于”
tab1,tab2,tab3 = st.tabs(["数据预览","分组", "关于"])

  
class FileUploader:
    def __init__(self):
        self.file = None
        
    def upload(self):
        uploaded_file = st.sidebar.file_uploader("上传文件", type=["xls", "xlsx"])
        if uploaded_file is not None:
            self.file = pd.ExcelFile(uploaded_file)
        else:
            st.write("请上传文件")

file_uploader = FileUploader()
file_uploader.upload()


# tab1用于预览数据，使用st.dataframe,放置一个下拉菜单，用于选择excel文件中不同的sheet，默认为第一个sheet
# tab1用于预览数据，使用st.dataframe,放置一个下拉菜单，用于选择excel文件中不同的sheet，默认为第一个sheet
class DataPreview(FileUploader):
    def __init__(self):
        super().__init__()
        self.sheet_names = None
        self.selected_sheet = None

    def get_sheet_names(self):
        if self.file is not None:
            self.sheet_names = pd.ExcelFile(self.file).sheet_names

    def select_sheet(self):
        if self.sheet_names is not None:
            self.selected_sheet = st.sidebar.selectbox("选择一个sheet", self.sheet_names, index=0)

    def display_data(self):
        if self.selected_sheet is not None:
            data = pd.read_excel(self.file, sheet_name=self.selected_sheet)
            st.dataframe(data)

data_preview = DataPreview()
data_preview.get_sheet_names()
data_preview.select_sheet()

with tab1:
    data_preview.display_data()


#%%
# 使用pandas读取raw_data
df = pd.ExcelFile("raw_data.xlsx")
#%%


class VitalSigns(FileUploader):

    def __init__(self):

        super().__init__()

        self.sheet_names = None

        self.selected_sheet = None

        self.subject_id = None

        self.ND = None



    def get_sheet_names(self):

        if self.file is not None:

            self.sheet_names = pd.ExcelFile(self.file).sheet_names



    def select_sheet(self):

        if self.sheet_names is not None:

            self.selected_sheet = st.sidebar.selectbox("选择一个sheet", self.sheet_names, index=0)



    def set_subject_id(self):

        self.subject_id = st.sidebar.text_input("请输入subject_id")



    def set_ND(self):

        self.ND = st.sidebar.text_input("请输入ND")



    def extract_dfs(self):

        dfs_dict = {}

        for sheet_name in self.sheet_names:

            if "生命体征" in sheet_name:

                dfs_dict[sheet_name] = pd.read_excel(self.file, sheet_name=sheet_name)

        return dfs_dict



    def set_index(self, dfs_dict):

        for key in dfs_dict:

            dfs_dict[key].set_index(self.subject_id, inplace=True)



    def replace_ND(self, dfs_dict):

        for key in dfs_dict:

            dfs_dict[key].replace(self.ND, np.nan, inplace=True)



    def drop_columns(self, dfs_dict):

        for key in dfs_dict:

            dfs_dict[key].drop(columns=["是否进行生命体征检查", "检查日期"], inplace=True)



    def display_data(self, dfs_dict):

        if self.selected_sheet is not None:

            data = dfs_dict[self.selected_sheet]

            st.dataframe(data)



vital_signs = VitalSigns()

vital_signs.upload()

vital_signs.get_sheet_names()

vital_signs.select_sheet()

vital_signs.set_subject_id()

vital_signs.set_ND()

dfs_dict = vital_signs.extract_dfs()

vital_signs.set_index(dfs_dict)

vital_signs.replace_ND(dfs_dict)

vital_signs.drop_columns(dfs_dict)

vital_signs.display_data(dfs_dict)




 



class VitalSignsMerger(VitalSigns):

    def __init__(self):

        super().__init__()

        self.merged_dict = {}



    def merge_dfs(self):

        for key in self.dfs_dict:

            for col in self.dfs_dict[key].columns:

                if col not in self.merged_dict:

                    self.merged_dict[col] = self.dfs_dict[key][col]

                else:

                    self.merged_dict[col] = pd.concat([self.merged_dict[col], self.dfs_dict[key][col]], axis=1)



    def add_mean_column(self):

        for column, merged_df in self.merged_dict.items():

            row_means = merged_df.apply(lambda x: pd.to_numeric(x, errors='coerce').sum() / pd.to_numeric(x, errors='coerce').count() if pd.to_numeric(x, errors='coerce').count() != 0 else float('nan'), axis=1)

            merged_df.insert(len(merged_df.columns), str(column) + "_mean", row_means)



    def save_to_excel(self):

        with pd.ExcelWriter("vitalsigns.xlsx") as writer:

            for key in self.merged_dict:

                self.merged_dict[key].to_excel(writer, sheet_name=key)



vital_signs_merger = VitalSignsMerger()



def merge_vital_signs():

    vital_signs_merger.upload()

    vital_signs_merger.get_sheet_names()

    vital_signs_merger.select_sheet()

    vital_signs_merger.set_subject_id()

    vital_signs_merger.set_ND()

    vital_signs_merger.extract_dfs()

    vital_signs_merger.set_index()

    vital_signs_merger.replace_ND()

    vital_signs_merger.drop_columns()

    vital_signs_merger.merge_dfs()

    vital_signs_merger.add_mean_column()

    vital_signs_merger.save_to_excel()



with tab2:

    st.button("合并生命体征数据", on_click=merge_vital_signs)




    vital_signs_merger.save_to_excel()
