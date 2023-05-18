#%%
#%%
import numpy as np
import pandas as pd
import streamlit as st


 
# 设置streamlit的网页标题为“优卓医药科技”
st.set_page_config(page_title="优卓医药科技")



# 分文两个tab，第一个tab名称为“分组”，第二个tab名称为“关于”
tab1,tab2,tab3 = st.tabs(["数据预览","分组", "关于"])

  # 定义一个class，在st.sidebar中中用于上传excel，并显示文件名
class FileUploader:
    def __init__(self):
        self.file = None

    def run_1(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"],key="upforgroup")
        if self.file is not None:
            st.sidebar.write(self.file.name)
            
        else:
            st.sidebar.write("未上传文件")
            
        


# 实例化并调用


# ______________________________________



class SheetSelector(FileUploader):
    def __init__(self):
        
        self.sheet_names = None
        self.selected_sheet = None
    def run_2(self):
        if self.file is not None:
            self.sheet_names = pd.ExcelFile(self.file).sheet_names
            self.selected_sheet = st.selectbox("选择一个sheet", self.sheet_names)
            # 用空白替换掉sheet中的NaN，赋值给exhibition_data
            exhibition_data = pd.read_excel(self.file, sheet_name=self.selected_sheet, header=0).fillna("")
            st.dataframe(exhibition_data)
            return self.file
        


# 实例化并调用




#%%

class Group(SheetSelector):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.merged_dict = {}
        self.merging_dict = {}


    def refine(self,common_name,index_name):

        if self.file is not None:
            self.file = pd.ExcelFile(self.file)
            sheet_names = [sheet_name for sheet_name in self.file.sheet_names if str(common_name) in sheet_name]
            # 遍历sheet_names，将每个sheet另存为一个新的dataframe，命名为“第{i}周期用药情况”
            for i, sheet_name in enumerate(sheet_names, start=1):
                self.merged_dict[str(i)+str(common_name)] = self.file.parse(sheet_name)
                # 设置列名为“subject_id”的列为索引
                self.merged_dict[str(i)+common_name].set_index(str(index_name), inplace=True)
        else:
            st.write("请先上传文件")

    def process(self,na_rep):
        for key in self.merged_dict:
            self.merged_dict[key].replace(to_replace=na_rep, value=np.nan, inplace=True)

        

    def merge(self):
        for key in self.merged_dict:
            for column in self.merged_dict[key].columns:
                if column not in self.merging_dict:
                    self.merging_dict[column] = pd.DataFrame(self.merged_dict[key][column])
                else:
                    self.merging_dict[column] = pd.concat([self.merging_dict[column], pd.DataFrame(self.merged_dict[key][column])], axis=0)
            self.merging_dict = {k: v.reset_index(drop=True) for k, v in self.merging_dict.items()}

 

    def mean(self, select_columns):
        for key in self.merging_dict:
            for column in self.merging_dict[key].columns:
                if column not in select_columns:
                    self.merging_dict[key] = self.merging_dict[key].drop(column, axis=1)

        self.merging_dict = {k: v.reset_index(drop=True) for k, v in self.merging_dict.items()}
        for key in self.merging_dict:
            row_means = self.merging_dict[key].apply(lambda x: pd.to_numeric(x, errors='coerce').sum() / pd.to_numeric(x, errors='coerce').count() if pd.to_numeric(x, errors='coerce').count() != 0 else float('nan'), axis=1)
            self.merging_dict[key].insert(len(self.merging_dict[key].columns), str(key) + "_mean", row_means)
        return self.merging_dict
    
 
class NewGroup(Group):
    def __init__(self):
        super().__init__()
        
    def show(self):
        for key in self.merging_dict:
            st.write(key)
            st.table(self.merging_dict[key])

 
class ExcelWriter(NewGroup):
    def __init__(self):
        super().__init__()
        
    def write_to_excel(self):
        if self.file is not None:
            with pd.ExcelWriter("output.xlsx") as writer:
                for key in self.merging_dict:
                    self.merging_dict[key].to_excel(writer, sheet_name=key)
            st.download_button(label="下载结果", data="output.xlsx", file_name="output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.write("请先上传文件")



# 实例化并调用


