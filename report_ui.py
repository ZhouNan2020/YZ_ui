

import streamlit as st
import pandas as pd
import numpy as np

class MyApp:
    def __init__(self):
        self.file = None
        self.sheetdict = {}
        self.sheet_selected = None
        self.col_selected = None
        self.df_final = None
        self.dfdict = None

    def run(self):
        st.set_page_config(page_title="My App", page_icon=":guardsman:", layout="wide", initial_sidebar_state="expanded", )
        st.markdown(
            """
            <style>
            .reportview-container {
                background: #FFFACD
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        self.sidebar()

        tabs = ["数据预览", "按索引筛选", "复杂分组",'多个试验组的复杂分组']
        st.sidebar.title("导航")
        selected_tab = st.sidebar.radio("选择一个标签页", tabs)

        if selected_tab == "数据预览":
            self.tab1()
        elif selected_tab =="按索引筛选":
            self.tab2()
        elif selected_tab ==  "复杂分组":
            self.tab3()
        elif selected_tab ==  '多个试验组的复杂分组':
            self.tab4()

    def sidebar(self):
        st.sidebar.title("上传文件")
        self.file = st.sidebar.file_uploader("选择一个文件", type=["xls", "xlsx"])

    def tab1(self):
        if self.file is not None:
            self.sheet_names = pd.ExcelFile(self.file).sheet_names
            self.sheet_selected = st.selectbox("选择一个sheet", self.sheet_names)
            df = pd.read_excel(self.file, sheet_name=self.sheet_selected)
            st.write(df)
        else:
            st.warning("请先上传文件。")

    def tab2(self):
            st.title("按索引筛选")
            st.write("请上传索引文件")
            self.index = st.file_uploader("选择一个文件", type=["xls", "xlsx"],key='tab3')

            if st.button("开始筛选"):
                if self.index is not None: #如果上传了索引文件
                    index_df = pd.read_excel(self.index) #读取索引文件
                    if "subject_id" in index_df.columns: #如果索引文件中有subject_id列
                        if self.file is not None: #如果上传了筛选文件
                            sheet_names = pd.ExcelFile(self.file).sheet_names #获取筛选文件中的sheet名
                            sheet_dict = {} #创建一个空字典，用于存储筛选后的数据
                            for sheet in sheet_names: #遍历筛选文件中的每个sheet
                                df = pd.read_excel(self.file, sheet_name=sheet) #读取当前sheet的数据
                                if "subject_id" in df.columns: #如果当前sheet中有subject_id列
                                    df_filtered = df[df["subject_id"].isin(index_df["subject_id"])] #筛选出subject_id列中包含在索引文件中的数据
                                    sheet_dict[sheet] = df_filtered #将筛选后的数据添加到字典中
                            if len(sheet_dict) > 0: #如果筛选后的数据字典不为空
                                #selected_sheet = st.selectbox("选择一个sheet", list(sheet_dict.keys())) #创建一个下拉选择菜单，用于选择字典中不同的key所对应的df
                                #st.dataframe(sheet_dict[selected_sheet]) #在页面上显示选择的df
                                with pd.ExcelWriter('filterdata.xlsx') as writer: #将字典写入一个excel，不用的key对应excel中不同的sheet名称，命名为filterdata，供用户下载
                                    for key in sheet_dict.keys():
                                        sheet_dict[key].to_excel(writer, sheet_name=key, index=False)
                                st.download_button( #添加一个下载按钮，用于下载筛选后的数据
                                    label="下载结果",
                                    data=open('filterdata.xlsx', 'rb').read(),
                                    file_name="filterdata.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )

                            else: #如果筛选后的数据列表为空
                                st.warning("没有找到subject_id列")
                        else: #如果没有上传筛选文件
                            st.warning("请先上传文件。")
                    else: #如果索引文件中没有subject_id列
                        st.warning("索引文件中没有subject_id列")
                else: #如果没有上传索引文件
                    st.warning("请先上传索引文件。")


    def tab3(self):
        if self.file is not None:
            self.sheet_names = pd.ExcelFile(self.file).sheet_names
            sheet_selected = st.multiselect("选择sheet", self.sheet_names, key="sheetname")
            for sheet in sheet_selected:
                self.sheetdict[sheet] = pd.read_excel(self.file, sheet_name=sheet)
            colnames = []
            for sheet in self.sheetdict:
                for col in self.sheetdict[sheet].columns:
                    if col not in colnames:
                        colnames.append(col)
            self.col_selected = st.multiselect("选择列", colnames, key="colname")
            if st.button("开始计算"):
                df_list = []
                for sheet in self.sheetdict:
                    df = self.sheetdict[sheet][self.col_selected]
                    df = df.replace(['', 'ND'], np.nan)
                    df_new = pd.DataFrame()
                    for col in df.columns:
                        non_null_count = df[col].count()
                        mean = pd.to_numeric(df[col], errors='coerce').mean(skipna=True)
                        std = pd.to_numeric(df[col], errors='coerce').std(skipna=True)
                        median = pd.to_numeric(df[col], errors='coerce').median(skipna=True)
                        mean_plus_std = f"{mean:.2f}±{std:.2f}"
                        max_val = pd.to_numeric(df[col], errors='coerce').max(skipna=True)
                        min_val = pd.to_numeric(df[col], errors='coerce').min(skipna=True)
                        df_new[col] = [non_null_count, round(mean,2),mean_plus_std, round(median,2), round(max_val,2), round(min_val,2)]
                    df_new["sheet"] = sheet
                    df_new["统计值"] = ["非空值计数", "平均值", "平均值±标准差", "中位数", "最大值", "最小值"]
                    df_new = df_new[["统计值"] + list(df_new.columns[:-1])]
                    df_new = df_new.set_index('sheet')
                    df_list.append(df_new)

                self.df_final = pd.concat(df_list, axis=0)
                st.dataframe(self.df_final)
                st.download_button(
                    label="下载结果",
                    data=self.df_final.to_csv(index=False).encode(),
                    file_name="finaldata.csv",
                    mime="text/csv"
                )

        else:
            st.warning("请先上传文件。")
    
    

    def tab4(self):
        
        st.markdown("**请选择分组参考列**")
        groupsheet = st.selectbox("选择一个sheet", self.sheet_names, key="groupsheet")
        groupcol = st.selectbox("选择一个列", self.sheetdict[groupsheet].columns, key="groupcol")
        if st.button("开始分组"):
            self.dfdict = {}
            for sheet in self.sheetdict:
                self.dfdict[sheet] = pd.read_excel(self.file, sheet_name=sheet)
            group_df = self.sheetdict[groupsheet][groupcol]
            for key in self.dfdict:
                self.dfdict[key] = pd.merge(self.dfdict[key], group_df, on='subject_id', how='left')
            group_dict = {}
            for key in self.dfdict:
                group_dict[key] = {k: v.to_dict('records') for k, v in self.dfdict[key].groupby(groupcol)}
            self.dfdict = group_dict


    def tab4(self):
        st.markdown("**请选择分组参考列**")
        groupsheet = st.selectbox("选择一个sheet", self.sheet_names, key="groupsheet")
        groupcol = st.selectbox("选择一个列", self.sheetdict[groupsheet].columns, key="groupcol")
        if st.button("开始分组"):
            self.dfdict = {}
            for sheet in self.sheetdict:
                self.dfdict[sheet] = pd.read_excel(self.file, sheet_name=sheet)
            group_df = self.sheetdict[groupsheet][groupcol]
            for key in self.dfdict:
                self.dfdict[key] = pd.merge(self.dfdict[key], group_df, on='subject_id', how='left')
            group_dict = {}
            for key in self.dfdict:
                group_dict[key] = {k: v.to_dict('records') for k, v in self.dfdict[key].groupby(groupcol)}
            self.dfdict = group_dict
            
            valuedict = {}
            for key in self.dfdict:
                valuedict[key] = self.dfdict[key]
            tab4_sheetname = st.multiselect("选择一个sheet", list(valuedict.keys()), key="tab4_sheetname")
            if st.button("选择完成"):
                valuedict = {}
                for sheet in tab4_sheetname:
                    valuedict[sheet] = self.dfdict[sheet]
                colnames = []
                for sheet in valuedict:
                    for col in valuedict[sheet][0].keys():
                        if col not in colnames:
                            colnames.append(col)
                valuedict_new = []
                for sheet in valuedict:
                    df = pd.DataFrame(valuedict[sheet])
                    valuedict_new.append(df)
                valuedict = pd.concat(valuedict_new, axis=0)
                valuedict = valuedict[colnames]
                valuedict = valuedict.drop_duplicates()
                valuedict = valuedict.to_dict('list')
                
                tab4_colname = st.multiselect("选择一个列", list(valuedict.keys()), key="tab4_colname")
                if st.button("选择完成"):
                    valuedict_new = {}
                    for col in tab4_colname:
                        valuedict_new[col] = valuedict[col]
                    valuedict = valuedict_new
                    self.dfdict = valuedict

        


        
        

        

        



    


if __name__ == "__main__":
    app = MyApp()
    app.run()
