




from flask import Flask, render_template, request, redirect, url_for, session
import streamlit as st

app = Flask(__name__)

class MyApp:
    def __init__(self):
        self.file = None
        self.sheetdict = {}
        self.sheet_selected = None
        self.col_selected = []
        self.df_final = None
        self.dfdict = {}
        self.sheet_names = None
        self.sheet_names_tab3 = []
        self.index = None
        self.sheet_names_tab4 = None
        self.selectedsheet = {}
        self.tab3colnames = []
        

    def run(self):
        st.set_page_config(page_title="优卓医药科技", page_icon=":guardsman:", layout="wide", initial_sidebar_state="expanded", )
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

        tabs = ["关于","数据预览", "按索引筛选", "复杂分组",'划分试验组','多试验组的计数统计','哑变量转换','每周期用药人数计算']
        st.sidebar.title("导航")
        selected_tab = st.sidebar.radio("选择一个标签页", tabs)

        if selected_tab =="关于":
            self.tabintro()
        elif selected_tab == "数据预览":
            self.tab1()
        elif selected_tab =="按索引筛选":
            self.tab2()
        elif selected_tab ==  "复杂分组":
            self.tab3()
        elif selected_tab ==  '划分试验组':
            self.tab4()
        elif selected_tab == '多试验组的计数统计':
            self.tab5()
        elif selected_tab == '哑变量转换':
            self.tab6()
        elif selected_tab == '每周期用药人数计算':
            self.tab7()

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/tabintro')
    def tabintro():
        st.subheader("更新日志")
        st.markdown('**2023年5月26日：**') #将日期加粗
        st.markdown('1.增加哑变量转换模块，用于subject_id不唯一的分组预处理')
        st.markdown('2.增加每周期用药人数计算模块，用于计算每周期用药人数及占比')     

if __name__ == '__main__':
    app.run(debug=True)


