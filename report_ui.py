


import streamlit as st
import pandas as pd

import streamlit as st
import pandas as pd

class MyApp:
    def __init__(self):
        self.file = None
        self.sheetdict = {}
        self.sheet_selected = None
        self.col_selected = None
        self.df_final = None

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

        tabs = ["数据预览", "复杂分组", "Tab 3"]
        st.sidebar.title("导航")
        selected_tab = st.sidebar.radio("选择一个标签页", tabs)

        if selected_tab == "数据预览":
            self.tab1()
        elif selected_tab == "复杂分组":
            self.tab2()
        elif selected_tab == "Tab 3":
            self.tab3()

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
                    df_new = pd.DataFrame()
                    for col in df.columns:
                        df_mean = str(round(df[col].mean(), 2))
                        df_std = str(round(df[col].std(), 2))
                        df_std_str = str(df_mean) + "±" + str(df_std)
                        df_median = str(round(df[col].median(), 2))
                        df_max = str(round(df[col].max(), 2))
                        df_min = str(round(df[col].min(), 2))
                        df_new[col] = [df_mean, df_std_str, df_median, df_max, df_min]

                    df_new["sheet"] = sheet
                    df_new["column"] = df_new.index
                    df_new = df_new.reset_index(drop=True)
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


    def tab3(self):
        st.write("This is Tab 3")

if __name__ == "__main__":
    app = MyApp()
    app.run()


