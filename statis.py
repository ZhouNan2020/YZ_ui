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

    def run(self):
        self.file = st.sidebar.file_uploader("上传excel文件", type=["xlsx", "xls"])
        if self.file is not None:
            st.sidebar.write(self.file.name)
            
        else:
            st.sidebar.write("未上传文件")
            
        


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
            return self.file
        


# 实例化并调用
with tab1:
    sheet_selector = SheetSelector(file_uploader.file)
    sheet_selector.run()



#%%

class Group(FileUploader):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.merged_dict = {}
        

    
    def refine(self,common_name):
        if self.file is not None:
            self.file = pd.ExcelFile(self.file)
        
            for sheet_name in self.file.sheet_names:
                if common_name in sheet_name:
                    self.data[sheet_name] = pd.ExcelFile(self.file, sheet_name=sheet_name)
        else:
            st.write("请先上传文件")

    def process(self,index_name,na_rep,drop_columns):
        for key in self.data:
            self.data[key].set_index(index_name, inplace=True)
        for key in self.data:
            self.data[key].replace(na_rep, np.nan, inplace=True)
        if drop_columns=="":
            pass
        else:
            for key in self.data:
                self.data[key].drop(columns=list(drop_columns), inplace=True)
    
    def merge(self):
        
        for key in self.data:
            for col in self.data[key].columns:
                if col not in self.merged_dict:
                    self.merged_dict[col] = self.data[key][col]
                else:
                    self.merged_dict[col] = pd.concat([self.merged_dict[col], self.data[key][col]], axis=1)

    def mean(self):
        for column, merged_df in self.merged_dict.items():
            row_means = merged_df.apply(lambda x: pd.to_numeric(x, errors='coerce').sum() / pd.to_numeric(x, errors='coerce').count() if pd.to_numeric(x, errors='coerce').count() != 0 else float('nan'), axis=1)
            merged_df.insert(len(merged_df.columns), str(column) + "_mean", row_means)


        
with tab2:
    common_name = st.text_input("要提取的sheet名称中的通用字符")
    index_name = st.text_input("索引列名称")
    na_rep = st.text_input("空值符号")
    drop_columns = st.text_input("是否有需要删除的列（请连续输入，以英文逗号分隔，例如：是否进行生命体征检查, 检查日期）")
    group = Group()
    

    if st.button("输入完成并执行"):
        group.refine(common_name)
        group.process(index_name,na_rep,drop_columns)
        group.merge()
        group.mean()
        st.write(group.merged_dict)
        st.write(common_name)
        st.write(group.file)
        st.write(group.data)
    


    
    
 
class Download:
    def __init__(self, merged_dict):
        self.merged_dict = merged_dict

    def run(self):
        if self.merged_dict is not None:
            if st.button("下载确认好的数据"):
                with pd.ExcelWriter("vitalsigns.xlsx") as writer:
                    for key in self.merged_dict:
                        self.merged_dict[key].to_excel(writer, sheet_name=key)

# 实例化并调用

    # 提供一个button，实例化并调用
    


    