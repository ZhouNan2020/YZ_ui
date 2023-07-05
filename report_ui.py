
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
import zipfile
import statsmodels.api as sm
import statsmodels.formula.api as smf
#%%
# 设置plt中文显示和负号显示
font = font_manager.FontProperties(fname='simhei.ttf')

parameters = {'xtick.labelsize': 20,
              'ytick.labelsize': 20,
              
              'axes.unicode_minus':False}
plt.rcParams.update(parameters)


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

        tabs = ["关于","数据预览", "Chat with AI", "按索引筛选", "复杂分组",'划分试验组','多试验组的计数统计','哑变量转换','每周期用药人数计算','ECOG计数',"科瑞德不分组计数统计","科瑞德分组计数统计","湖南省肿瘤肝癌项目基线统计"
                ,"湖南省肿瘤肝癌项目疗效评价计数","湖南省肿瘤肝癌项目肿瘤诊断计数","湖南省肿瘤肝癌项目血常规统计","中介效应与调节效应计算"]
        st.sidebar.title("导航")
        selected_tab = st.sidebar.radio("选择一个功能模块", tabs)

        if selected_tab =="关于":
            self.tabintro()
        
        elif selected_tab == "数据预览":
            self.tab1()
        elif selected_tab =="Chat with AI":
            self.tabchat()
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
        elif selected_tab == 'ECOG计数':
            self.tab8()
        elif selected_tab == '科睿德不分组计数统计':
            self.tab9()
        elif selected_tab == '科睿德分组计数统计':
            self.tab10()
        elif selected_tab == '湖南省肿瘤肝癌项目基线统计':
            self.tab11()
        elif selected_tab == '湖南省肿瘤肝癌项目疗效评价计数':
            self.tab12()
        elif selected_tab == '湖南省肿瘤肝癌项目肿瘤诊断计数':
            self.tab13()
        elif selected_tab == '湖南省肿瘤肝癌项目血常规统计':
            self.tab14()
        elif selected_tab == '中介效应与调节效应计算':
            self.tab15()
            

    def tabintro(self):
        
        st.subheader('更新日志')
        st.markdown('**2023年6月28日：**') #将日期加粗
        st.markdown('1.增加了湖南省肿瘤肝癌项目疗效评价计数模块')
        st.markdown('2.增加了湖南省肿瘤肝癌项目肿瘤诊断计数模块')
        st.markdown('3.增加了湖南省肿瘤肝癌项目血常规统计模块')
        st.markdown('**2023年6月26日：**') #将日期加粗
        st.markdown('1.增加了湖南省肿瘤基线统计模块')
        st.markdown('**2023年6月6日：**') #将日期加粗
        st.markdown('1.增加了科睿德不分组计数统计模块')
        st.markdown('2.增加了科睿德分组计数统计模块')
        st.markdown('**2023年6月5日：**') #将日期加粗
        st.markdown('1.接入GPT模型，开放chat with AI模块')
        st.markdown('**2023年6月1日：**') #将日期加粗
        
        st.markdown('1.之前“按索引筛选”模块和“复杂分组”模块产出结果的文件名太相似了，现更改“按索引筛选”模块产出结果的文件名为“筛选后数据.xlsx”')
        st.markdown('2.移除“复杂分组”模块计算结果中的均值')
        st.markdown('**2023年5月31日：**') #将日期加粗
        st.markdown('1.给部分模块增加了解释性图例')
        st.markdown('2.复杂分组模块计算结果中将统计值以英文表示') #将日期加粗
        st.markdown('**2023年5月29日：**') #将日期加粗
        st.markdown('1.增加ECOG评分计数模块')
        st.markdown('**2023年5月26日：**') #将日期加粗
        st.markdown('1.增加哑变量转换模块，用于subject_id不唯一的分组预处理')
        st.markdown('2.增加每周期用药人数计算模块，用于计算每周期用药人数及占比')     

    def sidebar(self):
        st.sidebar.title("上传文件")
        self.file = st.sidebar.file_uploader("选择一个文件", type=["xls", "xlsx"])
        if self.file is not None: #如果上传了文件
            self.sheetdict = pd.ExcelFile(self.file).parse(sheet_name=None) #使用pd.ExcelFile和parse方法读取文件中的所有sheet

    
    
    
    
    
    
    def tab1(self):
        
        if self.file is not None: #如果上传了文件
            self.sheet_names = list(self.sheetdict.keys()) #直接从self.sheetdict中读取不同的键
            sheet_selected = st.selectbox("选择一个sheet", self.sheet_names) #创建一个下拉选择菜单，用于选择不同的sheet
            if sheet_selected in self.sheetdict.keys(): #如果选择的sheet已经在self.sheetdict中存在
                st.write(self.sheetdict[sheet_selected]) #直接在页面上呈现对应的dataframe
                
        else: #如果没有上传文件
            st.warning("请先上传文件。")

    def tabchat(self):
        st.markdown('**注意**')
        st.markdown('在针对任何一个课题的数据处理中，应当优先使用具有针对性的模块，当现有模块无法解决问题/临时性需求时，才考虑使用AI模块')
        st.markdown('为了程序的稳定性，AI模块需要点击下方链接跳转')
        st.markdown('[点击跳转](https://zhounan2020-pythonproject-app-vbvbxd.streamlit.app/)')
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
                                    file_name="筛选后数据.xlsx",
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
        
        st.subheader('这个模块用来算下面这个表或类似的表')
 
        st.image('druguse.png',use_column_width=True)

        
        if self.file is not None: #如果上传了文件
            st.write('用于用药记录、生命体征等复杂分组')
            self.sheet_names_tab3 = pd.ExcelFile(self.file).sheet_names #获取文件中的所有sheet名
            sheet_selected = st.multiselect("选择sheet", self.sheet_names_tab3, key="sheetname") #创建一个多选框，用于选择不同的sheet

            for sheet in sheet_selected: #遍历选择的sheet
                self.selectedsheet[sheet] = pd.read_excel(self.file, sheet_name=sheet) #将选择的sheet读取到self.sheetdict中
             #创建一个空列表，用于存储所有的列名
            self.tab3colnames = []
            for sheet in self.selectedsheet: #遍历self.sheetdict中的每个sheet
                for col in self.selectedsheet[sheet].columns: #遍历当前sheet中的每一列
                    if col not in self.tab3colnames: #如果当前列名不在colnames中
                        self.tab3colnames.append(col) #将当前列名添加到colnames中

            self.col_selected = st.multiselect("选择列", self.tab3colnames, key="colname")
            if st.button("开始计算"):
                self.tab3df_list = []
                for sheet in self.selectedsheet: #遍历self.sheetdict中的每个sheet
                    if set(self.col_selected).issubset(set(self.selectedsheet[sheet].columns)): #如果self.col_selected中的所有列名都在self.sheetdict[sheet]的列名中
                        df = self.selectedsheet[sheet][self.col_selected] #获取当前sheet中self.col_selected列的数据
                        df = df.replace(['', 'ND'], np.nan) #将df中的空字符串和“ND”替换为nan
                        df_new = pd.DataFrame() #创建一个空dataframe，用于存储当前sheet的统计结果
                        for col in df.columns: #遍历df中的每一列
                            non_null_count = df[col].count() #获取当前列的非空值计数
                            mean = pd.to_numeric(df[col], errors='coerce').mean(skipna=True) #获取当前列的平均值
                            std = pd.to_numeric(df[col], errors='coerce').std(skipna=True) #获取当前列的标准差
                            median = pd.to_numeric(df[col], errors='coerce').median(skipna=True) #获取当前列的中位数
                            mean_plus_std = f"{mean:.2f}±{std:.2f}" #将平均值和标准差拼接成一个字符串
                            max_val = pd.to_numeric(df[col], errors='coerce').max(skipna=True) #获取当前列的最大值
                            min_val = pd.to_numeric(df[col], errors='coerce').min(skipna=True) #获取当前列的最小值
                            df_new[col] = [non_null_count, mean_plus_std, round(median,2), round(max_val,2), round(min_val,2)] #将当前列的统计结果添加到df_new中
                        df_new["sheet"] = sheet #添加一个名为“sheet”的列，值为当前sheet的名称
                        df_new["统计值"] = ["n",  "mean±std", "median", "max", "min"] #添加一个名为“统计值”的列，值为统计结果的名称
                        df_new = df_new[["统计值"] + list(df_new.columns[:-1])] #调整列的顺序
                        df_new = df_new.set_index('sheet') #将“sheet”列设置为索引
                        self.tab3df_list.append(df_new) #将当前sheet的统计结果添加到df_list中
                    else: #如果self.col_selected中的所有列名不都在self.sheetdict[sheet]的列名中
                        continue #跳过当前循环，执行下一个循环
                self.df_final = pd.concat(self.tab3df_list, axis=0) #将df_list中的所有dataframe合并成一个dataframe
                st.dataframe(self.df_final) #在页面上显示合并后的dataframe
                st.download_button(
                    label="下载结果",
                    data=self.df_final.to_csv(index=True).encode(),
                    file_name="finaldata.csv",
                    mime="text/csv"
                )
        else:
            st.warning("请先上传文件。")

        
        
    
    

    def tab4(self):
        
        st.write("注意：目前只支持将'subject_id'唯一的列作为分组依据")
        if self.file is not None:
            st.markdown("**请选择作为分组依据的列**")
            groupsheet = st.selectbox("选择分组依据列所在的sheet", list(self.sheetdict.keys()), key="groupsheet")
            groupcol = st.selectbox("选择分组依据列", self.sheetdict[groupsheet].columns, key="groupcol")
            if st.button("开始分组"):
                self.sheetdict = pd.ExcelFile(self.file).parse(sheet_name=None)
                for key in self.sheetdict.keys():
                    if 'subject_id' in self.sheetdict[key].columns:
                        self.sheetdict[key] = self.sheetdict[key].dropna(subset=['subject_id'])
                group_df = self.sheetdict[groupsheet][[groupcol,'subject_id']] #获取分组参考列的数据，并添加subject_id列
                group_df = group_df.fillna("未知") #将group_df中的nan值替换为字符串“未知”
                
                for key in list(self.sheetdict.keys()): #遍历dfdict中的每一个sheet
                    if key == groupsheet: #如果当前key等于groupsheet，则跳过当前循环，执行下一个循环
                        continue
                    elif 'subject_id' in self.sheetdict[key].columns: #如果self.sheetdict的key对应的dataframe中有列名为subject_id的列，则合并，如果没有，则删除这个key以及对应的值
                        # 将分组参考列的数据与dfdict中的数据进行合并，使用left join方式，以subject_id列为连接键
                        self.sheetdict[key] = pd.merge(group_df,self.sheetdict[key], on='subject_id', how='left') #将分组参考列的数据与dfdict中的数据进行合并
                    else:
                        del self.sheetdict[key]
                        continue #跳过当前循环，执行下一个循环
                    # 将分组后的数据转换为字典格式
                        #continue #如果self.sheetdict的key对应的dataframe中没有列名为subject_id的列，则删除这个key以及对应的值
                
                for key in self.sheetdict.keys():
                    if groupcol in self.sheetdict[key].columns: #如果self.sheetdict的key对应的dataframe中有列名为groupcol的列，则按照groupcol进行分组
                        self.sheetdict[key] = self.sheetdict[key].groupby(groupcol) #按照groupcol进行分组
                        # 将分组后的数据转换为字典格式
                self.sheetdict = {key: dict(list(group)) for key, group in self.sheetdict.items()}
                    #else:
                        #continue #如果self.sheetdict的key对应的dataframe中没有列名为groupcol的列，则执行下一个循环

                #self.sheetdict = {key: dict(list(group)) for key, group in self.sheetdict.items()} #将self.sheetdict中的数据转换为字典格式
                new_dict = {}
                for key, value in self.sheetdict.items():
                    for sub_key, sub_value in value.items():
                        if sub_key not in new_dict:
                            new_dict[sub_key] = {}
                        new_dict[sub_key][key] = sub_value

                self.dfdict = new_dict
                for key in new_dict.keys():
                    st.write(key)           
            if self.dfdict is not None:
                import zipfile
                with zipfile.ZipFile('excel.zip', 'w') as myzip:
                    for key in self.dfdict.keys():
                        writer = pd.ExcelWriter(f"{key}.xlsx")
                        for subkey in self.dfdict[key].keys():
                            df = self.dfdict[key][subkey]
                            df.to_excel(writer, sheet_name=subkey, index=False)
                        writer.save()
                        myzip.write(f"{key}.xlsx")
                st.download_button(
                    label="下载结果",
                    data=open('excel.zip', 'rb').read(),
                    file_name="excel.zip",
                    mime="application/zip"
                )

        else:
            st.warning("请先上传文件。")

            


    def tab5(self):
        
        st.write("注意：目前只支持将'subject_id'列为唯一值的sheet中的列作为分组依据")
        if self.file is not None: #如果self.file不为空
            self.tab5raw_data = pd.ExcelFile(self.file)
            for i in range(len(self.tab5raw_data.sheet_names)): #遍历excel文件中的每一个sheet
                sheet = self.tab5raw_data.parse(self.tab5raw_data.sheet_names[i]) #获取当前sheet的数据
                if 'subject_id' in sheet.columns: #如果当前sheet中有"subject_id"列
                    sheet.set_index('subject_id', inplace=True) #将"subject_id"列设置为索引列
                else: #如果当前sheet中没有"subject_id"列
                    del self.tab5raw_data.sheet_names[i] #删除当前sheet
            self.combinedata = pd.concat([self.tab5raw_data.parse(sheet_name) for sheet_name in self.tab5raw_data.sheet_names], axis=1, join='outer')
            self.combinedata = self.combinedata.loc[:,~self.combinedata.columns.duplicated()] 
            self.combinedata.dropna(subset=['subject_id'], inplace=True)
            #self.combinedata = self.combinedata.fillna("未知")
            st.write(self.combinedata)
            st.markdown("**请选择作为分组依据的列**") #在页面上显示文本
            self.tab5selectcol = st.selectbox("选择列", self.combinedata.columns, key="tab5selectcol") #提供一个下拉单选框，标签为“请选择作为分组依据的列”备选项是self.combinedata中的所有列，选择结果赋值给self.tab5selectcol
            st.markdown("**请选择需要进行描述性统计的列**") #在页面上显示文本
            self.tab5stacol = st.selectbox("选择列", self.combinedata.columns, key="tab5stacol") #提供第二个下拉单选框，标签为“请选择需要进行描述性统计的列”，赋值给self.tab5stacol
            #self.combinedata[self.tab5selectcol] = self.combinedata[self.tab5selectcol].fillna("未知") #将self.combinedata中的空值填充为“未知”

            ##self.sheetdict = pd.read_excel(self.file, sheet_name=None) #读取excel文件中的所有sheet，存入self.sheetdict中
            #for key in self.sheetdict.keys(): #遍历self.sheetdict中的每一个sheet
            #    if 'subject_id' in self.sheetdict[key].columns: #如果当前sheet中有subject_id列
            #        subject_id_cols = self.sheetdict[key].columns[self.sheetdict[key].columns == 'subject_id'] #获取所有subject_id列
            #        if len(subject_id_cols) > 1: #如果subject_id列的数量大于1
            #            self.sheetdict[key] = self.sheetdict[key].drop(subject_id_cols[1:], axis=1) #删除除第一个subject_id列以外的其他subject_id列
            #    else: #如果当前sheet中没有subject_id列
            #        continue #跳过当前循环，执行下一个循环
            #self.combinedata = pd.concat(self.sheetdict.values(), axis=1, join='outer', keys=self.sheetdict.keys()) #将self.sheetdict中的所有sheet横向合并成一个dataframe，on='subject_id'，how='outer'，命名为self.combinedata
 
        # 根据self.combinedata中self.tab5selectcol列值的不同，将self.combinedata分成不同的subdf，将所有的subdf存入一个字典，字典名为self.tab5groupdict
            self.tab5groupdict = dict(tuple(self.combinedata.groupby(self.tab5selectcol)))
            self.tab5datatype = st.radio("请选择数据类型", ("连续变量", "分类变量")) #提供一个st.radio，标签为“请选择数据类型”，备选项为“连续变量”，“分类变量”
            if st.button("开始计算"): #提供一个按钮：开始计算，用户点击后，执行以下操作
                if self.tab5datatype == "连续变量": #如果radio选择连续变量
                    sta_dict = {} #定义一个空字典sta_dict
                    for key in self.tab5groupdict.keys(): #遍历self.tab5groupdict中的每一个key
                        df = self.tab5groupdict[key] #获取当前key对应的dataframe
                        sta_df = df[[self.tab5stacol]] #获取需要进行描述性统计的列
                        sta_df_mean = sta_df.mean(skipna=True) #计算均值，不包括空值
                        sta_df_std = sta_df.std(skipna=True) #计算标准差，不包括空值
                        sta_df_median = sta_df.median(skipna=True) #计算中位数，不包括空值
                        sta_df_max = sta_df.max(skipna=True) #计算最大值，不包括空值
                        sta_df_min = sta_df.min(skipna=True) #计算最小值，不包括空值
                        sta_df_mean = sta_df_mean.round(2) #保留2位小数
                        sta_df_std = sta_df_std.round(2) #保留2位小数
                        sta_df_median = sta_df_median.round(2) #保留2位小数
                        sta_df_max = sta_df_max.round(2) #保留2位小数
                        sta_df_min = sta_df_min.round(2) #保留2位小数
                        staed_df = pd.DataFrame({'非空值计数': [sta_df.count(numeric_only=True).values[0]],
                                                 '均值': [sta_df_mean.mean(skipna=True)], #将计算结果存入hw_df中，不包括空值
                                              '均值±标准差': [f"{sta_df_mean[0]:.2f}±{sta_df_std[0]:.2f}"],
                                              '中位数': [sta_df_median[0]],
                                              '最大值': [sta_df_max[0]],
                                              '最小值': [sta_df_min[0]],
                                              },

                                             index=[str(self.tab5stacol)])
                        staed_df = staed_df.T #将sta_df转置
                        sta_dict[key] = staed_df #将sta_df存入sta_dict中
                   

                    writer = pd.ExcelWriter(f"{self.tab5stacol}.xlsx") #将sta_dict写入一个excel中，命名为self.tab5stacol.xlsx,sta_dict中不同的key，对应excel中不同的sheet
                    for key in sta_dict.keys():
                        key = key.replace('[','').replace(']','').replace(',','和').replace('"','').replace("'","") #将key中的"[]''"全部替换成无（不是空格），把“,”替换成“和”，将单引号和双引号替换成无（不是空格）
                        sta_dict[key].to_excel(writer, sheet_name=key, index=True) #将sta_dict[key]写入excel中，sheet名为key
                         #将sta_dict[key]写入excel中，sheet名为key
                    writer.save()

                    st.download_button( #提供st.download_button,使用户可以下载self.tab5stacol.xlsx到任意位置
                        label="下载结果",
                        data=open(f"{self.tab5stacol}.xlsx", 'rb').read(),
                        file_name=f"{self.tab5stacol}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                else: #如果radio选择分类变量
                
                    cate_dict = {}
                    for key in self.tab5groupdict.keys(): #遍历self.tab5groupdict中的每一个key
                        cate_df = self.tab5groupdict[key] #获取当前key对应的dataframe
                        
                        cate_df[self.tab5stacol].fillna('未知', inplace=True) #将self.tab5stacol列中的空值填充为“未知”
                        
                        cate_df_count = cate_df[self.tab5stacol].value_counts(dropna=True) #计算self.tab5stacol列中每个值的例数，不包括空值
                        cate_df_percent = cate_df[self.tab5stacol].value_counts(normalize=True, dropna=True) * 100 #计算self.tab5stacol列中每个值的占比，不包括空值
                        cate_df_percent = cate_df_percent.round(2) #保留2位小数
                        cate_count_df = pd.concat([cate_df_count, cate_df_percent], axis=1) #将cate_df_count和cate_df_percent合并成一个dataframe
                        cate_count_df.columns = ['例数', '占比(%)'] #将列名改为“例数”和“占比(%)”
                        cate_count_df['占比(%)'] = (cate_count_df['例数'] / cate_count_df['例数'].sum() * 100).apply(lambda x: f"{x:.2f}%") #计算占比列的值，占比=当前行在计数列的值/合计行计数列的值，占比列使用字符串百分比形式
                        cate_count_df.loc['合计'] = cate_count_df.sum() #计算每一列的合计值，并将合计值添加到cate_count_df的最后一行
                        cate_count_df.loc['合计', '占比(%)'] = '100%' #将合计行占比列的值改为“100%”

                        cate_dict[key] = cate_count_df #将cate_count_df存入cate_dict中
                    writer = pd.ExcelWriter(f"{self.tab5stacol}.xlsx") #将cate_dict写入一个excel中，命名为self.tab5stacol.xlsx,cate_dict中不同的key，对应excel中不同的sheet
                    for key in cate_dict.keys():
                        key = key.replace('[','').replace(']','').replace(',','和').replace('"','').replace("'","") #将key中的"[]''"全部替换成无（不是空格），把“,”替换成“和”，将单引号和双引号替换成无（不是空格）
                        cate_dict[key].to_excel(writer, sheet_name=key, index=True) #将cate_dict[key]写入excel中，sheet名为key
                    writer.save()



                    st.download_button( #提供st.download_button,使用户可以下载self.tab5stacol.xlsx到任意位置
                        label="下载结果",
                        data=open(f"{self.tab5stacol}.xlsx", 'rb').read(),
                        file_name=f"{self.tab5stacol}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            if st.button('额外统计：对年龄进行分层计数（仅用于优替）'):    
    
                def age_group(age):
                    try:
                        age = int(age)
                        if age >= 10 and age <= 30:
                            return '[10, 30]'
                        elif age > 30 and age <= 60:
                            return '(30, 60]'
                        elif age > 60:
                            return '>60'
                    except ValueError:
                        if 'UK' in str(age) or 'uk' in str(age):
                            return '未知'
                        else:
                            return '未知'

                age_dict = {}
                for key in self.tab5groupdict.keys():
                    df = self.tab5groupdict[key]
                    df['年龄_AGE'] = df['年龄_AGE'].apply(age_group)
                    age_count = df['年龄_AGE'].value_counts()
                    age_percent = df['年龄_AGE'].value_counts(normalize=True).apply(lambda x: f"{x*100:.2f}%")
                    age_df = pd.concat([age_count, age_percent], axis=1)
                    age_df.columns = ['计数', '占比']
                    age_dict[key] = age_df
                writer = pd.ExcelWriter('age.xlsx')
                for key in age_dict.keys():
                    key = key.replace('[','').replace(']','').replace(',','和').replace('"','').replace("'","")
                    age_dict[key].to_excel(writer, sheet_name=key, index=True)
                writer.save()

                st.download_button(
                    label="下载年龄的分层统计结果",
                    data=open('age.xlsx', 'rb').read(),
                    file_name='age.xlsx',
                    mime="application/vnd.ms-excel"
                )
        else:
            st.write('请先上传文件')

                    
    def tab6(self):
        
        st.write('将单个ID属于多个分组的情况转换为哑变量')
        
        if self.file is not None:
            tab6rawdata = pd.ExcelFile(self.file)
            tab6sheet_selected = st.selectbox("选择需要处理的sheet", tab6rawdata.sheet_names, key="tab6sheetname") #提供tab6rawdata中所有的sheet名称供选择，使用st,selectbox,
            tab6dummied_sheet = tab6rawdata.parse(tab6sheet_selected)
            dummycol = st.selectbox("选择需要转换为哑变量的列", tab6dummied_sheet.columns, key="tab6dummycol") #提供dummied_sheet中所有的列名称供选择，使用st,selectbox,
            if st.button('转换为哑变量'):
                tab6dummied_sheet = pd.get_dummies(tab6dummied_sheet, columns=[dummycol])
                tab6dummied_sheet = tab6dummied_sheet.groupby('subject_id').sum().reset_index()
                dummied_sheet_cols = [col for col in tab6dummied_sheet.columns if col.startswith(dummycol)]
                dummied_sheet_cols.append('subject_id')
                tab6dummied_sheet = tab6dummied_sheet[dummied_sheet_cols]
                tab6combinedata = pd.concat([tab6rawdata.parse(sheet_name) for sheet_name in tab6rawdata.sheet_names], axis=1, join='outer')
                tab6combinedata = tab6combinedata.loc[:,~tab6combinedata.columns.duplicated()]
                tab6combinedata = pd.merge(tab6combinedata, tab6dummied_sheet, how='outer', on='subject_id')
                def classify(df):
                    df['最终分类'] = ''

                    columns = [col for col in tab6dummied_sheet.columns if col != 'subject_id']

                    for i in range(len(df)):
                        if all(pd.isna(df.loc[df.index[i], col]) for col in columns):
                            df.loc[df.index[i], '最终分类'] = '未知'
                        else:
                            for col in columns:
                                if df.loc[df.index[i], col] != 0:
                                    df.loc[tab6combinedata.index[i], '最终分类'] += col.replace(dummycol, '') + '+'
                            df.loc[df.index[i], '最终分类'] = df.loc[df.index[i], '最终分类'][:-1]

                    return df
                tab6combinedata = classify(tab6combinedata)
                tab6combinedata = tab6combinedata.dropna(subset=['subject_id'])
    
                writer = pd.ExcelWriter(f"{dummycol}+哑变量.xlsx")
                tab6combinedata.to_excel(writer, sheet_name='哑变量', index=False)
                writer.save()

                st.download_button( #提供st.download_button,使用户可以下载xlsx格式的tab6combinedata，命名为“dummycol+哑变量.xlsx”
                    label="下载结果",
                    data=open(f"{dummycol}+哑变量.xlsx", 'rb').read(),
                    file_name=f"{dummycol}+哑变量.xlsx",
                    mime="application/vnd.ms-excel"
                )
        else:
            st.write('请先上传文件')




    def tab7(self):
        
        st.subheader('这个模块用来计算下面这个表')
        st.image('drugcount.png', use_column_width=True)

        
        if self.file is not None:
            st.write('每周期用药人数计算')
            self.sheet_names_tab3 = pd.ExcelFile(self.file).sheet_names #获取文件中的所有sheet名
            sheet_selected = st.multiselect("选择sheet", self.sheet_names_tab3, key="sheetname") #创建一个多选框，用于选择不同的sheet

            for sheet in sheet_selected: #遍历选择的sheet
                self.selectedsheet[sheet] = pd.read_excel(self.file, sheet_name=sheet) #将选择的sheet读取到self.sheetdict中
             #创建一个空列表，用于存储所有的列名
            self.tab3colnames = []
            for sheet in self.selectedsheet: #遍历self.sheetdict中的每个sheet
                for col in self.selectedsheet[sheet].columns: #遍历当前sheet中的每一列
                    if col not in self.tab3colnames: #如果当前列名不在colnames中
                        self.tab3colnames.append(col) #将当前列名添加到colnames中

            self.col_selected = st.multiselect("选择列", self.tab3colnames, key="colname")
            df_count = pd.DataFrame()
            if st.button("开始计算"):
                self.tab3df_list = []
                for sheet in self.selectedsheet: #遍历self.sheetdict中的每个sheet
                    if set(self.col_selected).issubset(set(self.selectedsheet[sheet].columns)): #如果self.col_selected中的所有列名都在self.sheetdict[sheet]的列名中
                        df = self.selectedsheet[sheet][self.col_selected] #获取当前sheet中self.col_selected列的数据
                        df_count = pd.concat([df_count, pd.DataFrame({'计数': [len(df.dropna())]}, index=[sheet])])
                        
                denominator = len(self.selectedsheet[sheet_selected[0]][self.col_selected]) #计算分母
                df_count['占比'] = df_count['计数'] / denominator * 100 #计算占比
                df_count['占比'] = df_count['占比'].apply(lambda x: '{:.2f}%'.format(x))
                st.write(df_count)

                if not df_count.empty:
                    writer = pd.ExcelWriter('用药周期人数计数.xlsx')
                    df_count.to_excel(writer, sheet_name='用药周期人数计数', index=True)
                    writer.save()
                    st.download_button(
                        label="下载用药周期人数计数",
                        data=open('用药周期人数计数.xlsx', 'rb').read(),
                        file_name='用药周期人数计数.xlsx',
                        mime="application/vnd.ms-excel"
                    )
        else:
            st.write('请先上传文件')






    def tab8(self):
        
 
        st.subheader('这个模块用来算下面这个表')
        st.image('ecog.png', use_column_width=True)

        
        if self.file is not None: #如果上传了文件
            if st.button('开始计算'):
                tab8df = pd.ExcelFile(self.file)
                tab8dfdict = {}
                for sheet_name in tab8df.sheet_names:
                    tab8dfdict[sheet_name] = tab8df.parse(sheet_name)
                ecog_dict = {}
                for sheet_name in tab8dfdict.keys():
                    if 'ECOG评分(若有)' in sheet_name:
                        ecog_dict[sheet_name] = tab8dfdict[sheet_name]
 
                tab8_count_dict = {}
                for key in ecog_dict.keys(): #遍历ecog_dict中的每个key
                    tab8_count_dict[key] = {} #为当前key创建一个空字典
                    df = ecog_dict[key] #获取当前key对应的DataFrame
                    count = df['评分结果'].value_counts() #计算评分结果的计数
                    count_df = pd.DataFrame({'计数': count, '占比': count/len(df)*100}) 
                    count_df['占比'] = count_df['占比'].apply(lambda x: '{:.2f}%'.format(x))
                    #占比只保留两位小数，且以百分数形式表示
                    tab8_count_dict[key]= count_df #将当前key对应的计数结果存储到ecog_count_dict中

                for key in tab8_count_dict.keys(): #遍历tab8_count_dict中的每一个key
                    df = tab8_count_dict[key] #获取当前key对应的DataFrame
                    df = df.sort_index() #将df的索引列按照数字从小到大的顺序排列  
                    tab8_count_dict[key] = df #将排序后的df存储回tab8_count_dict中
                tab8_combined_df = pd.concat([tab8_count_dict[key] for key in tab8_count_dict.keys()], axis=1, join='outer') #遍历tab8_count_dict中的每一个df，将这些df纵向合并，以列名为参考
                tab8_combined_df.columns = pd.MultiIndex.from_tuples([(key, col) for key in tab8_count_dict.keys() for col in tab8_count_dict[key].columns]) #将列名中的key和原始列名合并
                tab8_combined_df.loc['合计'] = tab8_combined_df.sum(numeric_only=True) #增加一行合计行在尾部，不对“占比”列执行sum
                #tab8_combined_df.loc['合计', ('占比', slice(None))] = tab8_combined_df.loc['合计', ('计数', slice(None))] / tab8_combined_df.loc['合计', ('计数', slice(None))].sum() * 100 #将占比列作为数字求值

                st.write(tab8_combined_df)
 
                st.download_button( #提供st.download_button,使用户可以下载csv格式的tab8_combined_df，命名为“ecog.csv”
                    label="下载结果",
                    data=tab8_combined_df.to_csv(index=True),
                    file_name="ecog.csv",
                    mime="text/csv"
                )
                st.write('下载结果后需要手动计算占比列的合计值')
        else:
            st.write('请先上传文件')
        
    def tab9(self):
        if self.file is not None:
            if st.button('开始计算'):
                krddata = pd.read_excel(self.file)
                # 将krddata中的NaN值和"UK"值均替换为“未知”
                #krddata = krddata.fillna('未知')
                #krddata = krddata.replace('UK', '未知')
                # 读取krddata中的“用药剂量”列，统计该列不同值的频次和占比，结果存储到一个df中，命名为useage_count_df，索引列为“用药剂量”中的不同值，列名为“计数”和“占比”
                useage_count_df = pd.DataFrame({'计数': krddata['用药剂量'].value_counts().round(1), '占比': (krddata['用药剂量'].value_counts()/len(krddata)*100).round(2).apply(lambda x: '{:.2f}%'.format(x))})
                # 将useage_count_df按照索引列的值从小到大排序
                useage_count_df = useage_count_df.sort_index()
                st.write(useage_count_df)
                # 读取krddata中的“日用药次数”列，统计该列不同值的频次和占比，结果存储到一个df中，命名为daily_count_df，索引列为“日用药次数”中的不同值，列名为“计数”和“占比”
                daily_count_df = pd.DataFrame({'计数': krddata['日用药次数'].value_counts().round(1), '占比': (krddata['日用药次数'].value_counts()/len(krddata)*100).round(2).apply(lambda x: '{:.2f}%'.format(x))})
                st.write(daily_count_df)
                # 重置daily_count_df的索引列，如果值为字符串“1”，则更改为字符串“每日一次';如果值为字符串“2”，则更改为字符串“每日两次”;如果值为字符串“3”，则更改为字符串“每日三次”;如果值为字符串“4”，则更改为字符串“每日四次”,依次类推。直到字符串“6”，“其它”仍然为“其它”，空值为”未知“
                #daily_count_df.index = daily_count_df.index.map({1: '每日一次', 2: '每日两次', 3: '每日三次', 4: '每日四次', 5: '每日五次', 6: '每日六次', '其它': '其它', np.nan: '未知'})
                # 读取krddata中的“用药量”列，统计该列不同值的频次和占比，结果存储到一个df中，命名为route_count_df，索引列为“用药量”中的不同值，列名为“计数”和“占比”
                route_count_df = pd.DataFrame({'计数': krddata['用药量'].value_counts().round(1), '占比': (krddata['用药量'].value_counts()/len(krddata)*100).round(2).apply(lambda x: '{:.2f}%'.format(x))})
                # 将route_count_df按照索引列的值从小到大排序，空值排在最后
                route_count_df = route_count_df.sort_index(na_position='last')
                st.write(route_count_df)
                # 处理krddata中“就诊日期”列，每个值只保留字符串中间代表月份的两位（原格式为xxxx-xx-xx）
                krddata['就诊日期'] = krddata['就诊日期'].str[5:7]
                krddata['就诊日期'] = krddata['就诊日期'].replace(['-U', 'UK'], '未知')
                # 将“就诊日期”列中的Nan值和空白值替换为“未知”
                krddata['就诊日期'] = krddata['就诊日期'].fillna('未知')
                # 按照月份对date进行分组，统计每个月份“用药量”列的总计和每个月份“用药量”列的总计占总体的比例，结果存储到一个df中，命名为month_count_df，索引列为月份，列名为“计数”和“占比”。
                month_count_df = pd.DataFrame({'计数': krddata.groupby('就诊日期')['用药量'].sum().round(1), '占比': (krddata.groupby('就诊日期')['用药量'].sum()/krddata['用药量'].sum()*100).round(2).apply(lambda x: '{:.2f}%'.format(x))})
                st.write(month_count_df)


                #将以上4个df保存到一个excel中，sheet_name分别为“用药剂量”，“给药频次分布”，“用药量情况”，'各月份用药情况“。然后提供st.download_button，使用户可以下载excel到任意本地路径
                with pd.ExcelWriter('output.xlsx') as writer:  
                    useage_count_df.to_excel(writer, sheet_name='用药剂量')
                    daily_count_df.to_excel(writer, sheet_name='给药频次分布')
                    route_count_df.to_excel(writer, sheet_name='用药量情况')
                    month_count_df.to_excel(writer, sheet_name='各月份用药情况')
                st.download_button( #提供st.download_button,使用户可以下载excel到任意本地路径
                    label="下载结果",
                    data=open('output.xlsx', 'rb').read(),
                    file_name="科睿德用药统计.xlsx",
                    mime="application/vnd.ms-excel"
                            )
        else:
            st.error("请上传科睿德的数据集")

    def tab10(self):
        if self.file is not None:
            krddata = pd.read_excel(self.file)
            # 将krddata中的NaN值和"UK"值均替换为“未知”
            krddata = krddata.fillna('未知')
            krddata = krddata.replace('UK', '未知')
            
            st.markdown("**请选择作为分组依据的列**")
            # 读取krddata的列名，存储到一个列表中，命名为col_list
            col_list = list(krddata.columns)
            # 使用st.selectbox()函数，备选项为col_list，命名为groupby_col
            groupby_col = st.selectbox('请选择作为分组依据的列', col_list)
        else:
            st.write('请先上传文件')
        if st.button("开始计算"):
                # 按照groupby_col的值不同，统计groupby_col中每个值对应的krddata的行数，并计算每个值对应的行数占krddata总行数的比例，结果存储到一个df中，命名为groupby_df，索引列为groupby_col，列名为“计数”和“占比”
                groupby_df = pd.DataFrame({'计数': krddata.groupby(groupby_col)[groupby_col].count(), '占比': (krddata.groupby(groupby_col)[groupby_col].count()/len(krddata)*100).round(2).apply(lambda x: '{:.2f}%'.format(x))})
                # 将索引列中的”UK“替换为”未知“，其它索引不变
                st.write(groupby_df)
                # 提取出krddata中“用药剂量”列，分别统计groupby_col中不同值对应的“用药剂量”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为”用药剂量“列的不同值，列为groupby_col的不同值的计数和占比

                cross_table = pd.crosstab(krddata['用药剂量'], krddata[groupby_col], margins=True, margins_name='总计')
                # 遍历cross_table的每个列，在每个列后面添加一个新列，命名为“占比”，值为该列的值除以该列的总计，结果保留两位小数，并转换为百分数
                useage_col_per = cross_table.apply(lambda x: x / len(krddata), axis=0)

                # 重新命名df_percent的列名，将列名后面添加“_占比”
                new_columns = [col + '_占比' for col in useage_col_per.columns]
                useage_col_per.columns = new_columns
                useage_with_percent = pd.concat([cross_table, useage_col_per], axis=1)
                # 重新排列df_with_percent的列顺序，将每个计数列与对应的占比列排在一起
                new_columns = []
                for col in useage_with_percent.columns:
                    if '占比' in col:
                        new_columns.append(col[:-3])
                        new_columns.append(col)
                useage_with_percent = useage_with_percent.reindex(columns=new_columns)
                # df_with_percent中所有”占比”列的值保留两位小数，以百分数表示
                for col in useage_with_percent.columns:
                    if '占比' in col:
                        useage_with_percent[col] = useage_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
                st.write(useage_with_percent)
                # 提取出krddata中的“日用药次数”列，分别统计groupby_col中不同值对应的“日用药次数”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“日用药次数”列的不同值，列为groupby_col的不同值的计数和占比
                count_cross_table = pd.crosstab(krddata['日用药次数'], krddata[groupby_col], margins=True, margins_name='总计')
                count_col_per = count_cross_table.apply(lambda x: x / len(krddata), axis=0)
                new_columns = [col + '_占比' for col in count_col_per.columns]
                count_col_per.columns = new_columns
                count_with_percent = pd.concat([count_cross_table, count_col_per], axis=1)
                new_columns = []
                for col in count_with_percent.columns:
                    if '占比' in col:
                        new_columns.append(col[:-3])
                        new_columns.append(col)
                count_with_percent = count_with_percent.reindex(columns=new_columns)
                for col in count_with_percent.columns:
                    if '占比' in col:
                        count_with_percent[col] = count_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
                st.write(count_with_percent)
                # 提取krddata中的“用药量”列，分别统计groupby_col中不同值对应的“用药量”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“用药量”列的不同值，列为groupby_col的不同值的计数和占比
                dose_cross_table = pd.crosstab(krddata['用药量'], krddata[groupby_col], margins=True, margins_name='总计')
                dose_col_per = dose_cross_table.apply(lambda x: x / len(krddata), axis=0)
                new_columns = [col + '_占比' for col in dose_col_per.columns]
                dose_col_per.columns = new_columns
                dose_with_percent = pd.concat([dose_cross_table, dose_col_per], axis=1)
                new_columns = []
                for col in dose_with_percent.columns:
                    if '占比' in col:
                        new_columns.append(col[:-3])
                        new_columns.append(col)
                dose_with_percent = dose_with_percent.reindex(columns=new_columns)
                for col in dose_with_percent.columns:
                    if '占比' in col:
                        dose_with_percent[col] = dose_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
                st.write(dose_with_percent)
                # 处理krddata中“就诊日期”列，每个值只保留字符串中间代表月份的两位（原格式为xxxx-xx-xx）
                krddata['就诊日期'] = krddata['就诊日期'].str[5:7]
                krddata['就诊日期'] = krddata['就诊日期'].apply(lambda x: int(x) if x.isdigit() else '未知')

                # 提取出krddata中的“就诊日期”列，分别统计groupby_col中不同值对应的“就诊日期”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“就诊日期”列的不同值，列为groupby_col的不同值的计数和占比
                date_cross_table = pd.crosstab(krddata['就诊日期'], krddata[groupby_col], margins=True, margins_name='总计')
                date_col_per = date_cross_table.apply(lambda x: x / len(krddata), axis=0)
                new_columns = [col + '_占比' for col in date_col_per.columns]
                date_col_per.columns = new_columns
                date_with_percent = pd.concat([date_cross_table, date_col_per], axis=1)
                new_columns = []
                for col in date_with_percent.columns:
                    if '占比' in col:
                        new_columns.append(col[:-3])
                        new_columns.append(col)
                date_with_percent = date_with_percent.reindex(columns=new_columns)
                for col in date_with_percent.columns:
                    if '占比' in col:
                        date_with_percent[col] = date_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
                st.write(date_with_percent)
                groupby_df
                useage_with_percent
                count_with_percent
                dose_with_percent
                date_with_percent
                # 将以上所有df写入excel文件中，每个df写入一个sheet
                with pd.ExcelWriter('output.xlsx') as writer:
                    groupby_df.to_excel(writer, sheet_name='分组')
                    useage_with_percent.to_excel(writer, sheet_name='剂量')
                    count_with_percent.to_excel(writer, sheet_name='频率')
                    dose_with_percent.to_excel(writer, sheet_name='用药量')
                    date_with_percent.to_excel(writer, sheet_name='月份')
                st.download_button( #提供st.download_button,使用户可以下载excel到任意本地路径
                    label="点击下载",
                    data=open('output.xlsx', 'rb').read(),
                    file_name='科睿德分组统计.xlsx',
                    mime='application/octet-stream'
                )
        if st.button('科睿德项目的年龄分层统计'):
            # 处理krddata的“年龄”列，将其中除了”未知“以外的值都转换为int类型
            krddata['年龄'] = krddata['年龄'].replace('未知', np.nan)
            krddata['年龄'] = krddata['年龄'].astype('float')
            # 遍历年龄列的值，将其分为4个层：10-30岁，30-60岁，60岁以上，未知
            age_list = []
            for age in krddata['年龄']:
                if np.isnan(age):
                    age_list.append('未知')
                elif 10<=age < 30:
                    age_list.append('10-30岁')
                elif 30<=age < 60:
                    age_list.append('30-60岁')
                else:
                    age_list.append('60岁以上')
            # 将分层后的年龄列表加入krddata中
            krddata['年龄分层'] = age_list
            # 按照“年龄分层”列的值不同，统计年龄分层中每个值对应的krddata的行数，并计算每个值对应的行数占krddata总行数的比例，结果存储到一个df中，命名为age_groupby_df
            age_groupby_df = pd.DataFrame(krddata.groupby('年龄分层').size(), columns=['数量'])
            age_groupby_df['占比'] = age_groupby_df['数量'] / len(krddata)
            age_groupby_df['占比'] = age_groupby_df['占比'].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write(age_groupby_df)
            # 提取出krddata中的“用药剂量”列，分别统计“年龄分层”列中不同值对应的“用药剂量”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“用药剂量”列的不同值，列为“年龄分层”的不同值的计数和占比
            dose_cross_table = pd.crosstab(krddata['用药剂量'], krddata['年龄分层'], margins=True, margins_name='总计')
            dose_col_per = dose_cross_table.apply(lambda x: x / len(krddata), axis=0)
            new_columns = [col + '_占比' for col in dose_col_per.columns]
            dose_col_per.columns = new_columns
            dose_with_percent = pd.concat([dose_cross_table, dose_col_per], axis=1)
            new_columns = []
            for col in dose_with_percent.columns:
                if '占比' in col:
                    new_columns.append(col[:-3])
                    new_columns.append(col)
            dose_with_percent = dose_with_percent.reindex(columns=new_columns)
            for col in dose_with_percent.columns:
                if '占比' in col:
                    dose_with_percent[col] = dose_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write(dose_with_percent)
            # 提取出krddata中的“日用药次数”列，分别统计“年龄分层”列中不同值对应的“日用药次数”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“日用药次数”列的不同值，列为“年龄分层”的不同值的计数和占比
            count_cross_table = pd.crosstab(krddata['日用药次数'], krddata['年龄分层'], margins=True, margins_name='总计')
            count_col_per = count_cross_table.apply(lambda x: x / len(krddata), axis=0)
            new_columns = [col + '_占比' for col in count_col_per.columns]
            count_col_per.columns = new_columns
            count_with_percent = pd.concat([count_cross_table, count_col_per], axis=1)
            new_columns = []
            for col in count_with_percent.columns:
                if '占比' in col:
                    new_columns.append(col[:-3])
                    new_columns.append(col)
            count_with_percent = count_with_percent.reindex(columns=new_columns)
            for col in count_with_percent.columns:
                if '占比' in col:
                    count_with_percent[col] = count_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write(count_with_percent)
            # 提取出krddata中的“用药量”列，分别统计“年龄分层”列中不同值对应的“用药量”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“用药量”列的不同值，列为“年龄分层”的不同值的计数和占比
            amount_cross_table = pd.crosstab(krddata['用药量'], krddata['年龄分层'], margins=True, margins_name='总计')
            amount_col_per = amount_cross_table.apply(lambda x: x / len(krddata), axis=0)
            new_columns = [col + '_占比' for col in amount_col_per.columns]
            amount_col_per.columns = new_columns
            amount_with_percent = pd.concat([amount_cross_table, amount_col_per], axis=1)
            new_columns = []
            for col in amount_with_percent.columns:
                if '占比' in col:
                    new_columns.append(col[:-3])
                    new_columns.append(col)
            amount_with_percent = amount_with_percent.reindex(columns=new_columns)
            for col in amount_with_percent.columns:
                if '占比' in col:
                    amount_with_percent[col] = amount_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write(amount_with_percent)
            # 处理krddata中“就诊日期”列，每个值只保留字符串中间代表月份的两位（原格式为xxxx-xx-xx）
            krddata['就诊日期'] = krddata['就诊日期'].apply(lambda x: x[5:7])
            
            krddata['就诊日期'] = krddata['就诊日期'].apply(lambda x: int(x) if x.isdigit() else '未知')
            
            # 提取出krddata中的“就诊日期”列，分别统计“年龄分层”列中不同值对应的“就诊日期”列的值的计数和该值计数占krddata总行数的占比，以cross_table的形式呈现，行为“就诊日期”列的不同值，列为“年龄分层”的不同值的计数和占比
            date_cross_table = pd.crosstab(krddata['就诊日期'], krddata['年龄分层'], margins=True, margins_name='总计')
            date_col_per = date_cross_table.apply(lambda x: x / len(krddata), axis=0)
            new_columns = [col + '_占比' for col in date_col_per.columns]
            date_col_per.columns = new_columns
            date_with_percent = pd.concat([date_cross_table, date_col_per], axis=1)
            new_columns = []
            for col in date_with_percent.columns:
                if '占比' in col:
                    new_columns.append(col[:-3])
                    new_columns.append(col)
            date_with_percent = date_with_percent.reindex(columns=new_columns)
            for col in date_with_percent.columns:
                if '占比' in col:
                    date_with_percent[col] = date_with_percent[col].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write(date_with_percent)
           
            # 将以上所有df写入excel文件中，每个df写入一个sheet
            with pd.ExcelWriter('output_2.xlsx') as writer:
                age_groupby_df.to_excel(writer, sheet_name='年龄分层')
                dose_with_percent.to_excel(writer, sheet_name='用药剂量')
                count_with_percent.to_excel(writer, sheet_name='日用药次数')
                amount_with_percent.to_excel(writer, sheet_name='总用药量')
                date_with_percent.to_excel(writer, sheet_name='就诊日期')
            st.download_button(
                label="点击下载",
                data=open('output_2.xlsx', 'rb').read(),
                file_name='科睿德年龄分层统计.xlsx',
                mime='application/octet-stream'
                ) 
   
   
   
   
    def tab11(self):
        if self.file is not None:
            # 使用pd.excelfile读取self.file
            tab11 = pd.ExcelFile(self.file)
            # 遍历tab11中的sheet，将其存入一个字典中，key对应sheet名称，value对应sheet中的df
            tab11_dict = {}
            for sheet in tab11.sheet_names:
                tab11_dict[sheet] = tab11.parse(sheet)
            # 从tab11_dict中提取出key名称中包含字符串“基本情况”的sheet，将其存入一个df名为tab11_basic中
            tab11_basic = tab11_dict[[sheet for sheet in tab11_dict.keys() if '基本情况' in sheet][0]]
            # 获取tab11_basic中名为“年龄”的列，将其转换为int类型，赋值给一个df名为age_df
            age_df = tab11_basic['年龄']#.astype(int)#
            # 计算age_df的非空值计数、均值、标准差，中位数，最大值，最小值，并且将这些统计量放入一个df中名为age_sta_df
            notnull_count = age_df.notnull().sum()
            mean = age_df.mean()
            std = age_df.std()
            mean_std = f"{mean:.2f}±{std:.2f}"
            age_sta_df = pd.DataFrame({'非空值计数': notnull_count, '均值±标准差': mean_std, '中位数': age_df.median(), '最大值': age_df.max(), '最小值': age_df.min()}, index=[0])
            age_sta_df = age_sta_df.round(2)
            # 转置这个表格
            age_sta_df = age_sta_df.T
            age_sta_df.columns = ['统计量']
            # 列名改为“统计量”
            st.write("年龄统计量:")
            st.write(age_sta_df)
            # 获取tab11_basic中名为“性别”的列，赋值给一个df名为sex_df
            sex_df = tab11_basic['性别']
            # 使用“未知”替换sex_df中的空值
            sex_df = sex_df.fillna('未知')
            sex_df = sex_df.apply(lambda x: '男性' if x == '男' else ('女性' if x == '女' else x))
            # 计算sex_df中不同值的计数和占比，占比=当前值的计数/sex_df中所有值的总计数。结果放入一个df名为sex_sta_df中
            sex_count = sex_df.value_counts()
            sex_per = sex_count / len(sex_df)
            sex_sta_df = pd.DataFrame({'计数': sex_count, '占比': sex_per})
            sex_sta_df.loc['合计'] = sex_sta_df.sum()
            sex_sta_df['占比'] = sex_sta_df['占比'].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write("性别统计量:")
            st.write(sex_sta_df)
            # 获取tab11_basic中名为“民族”的列，赋值给一个df名为nation_df
            nation_df = tab11_basic['民族']
            # 使用字符串“未知”替换nation_df中的空值
            nation_df = nation_df.fillna('未知')
            # 计算nation_df中不同值的计数和占比，占比=当前值的计数/nation_df中所有值的总计数。结果放入一个df名为nation_sta_df中
            nation_count = nation_df.value_counts()
            nation_per = nation_count / len(nation_df)
            nation_sta_df = pd.DataFrame({'计数': nation_count, '占比': nation_per})
            nation_sta_df.loc['合计'] = nation_sta_df.sum()
            nation_sta_df['占比'] = nation_sta_df['占比'].apply(lambda x: '{:.2f}%'.format(x*100))
            st.write("民族统计量:")
            st.write(nation_sta_df)
            # 获取tab11_basic中名为“身高”的列，赋值给一个df名为height_df
            height_df = tab11_basic['身高']
            # 设置height_df中的"uk","UK"为np.nan
            height_df = height_df.apply(lambda x: np.nan if x in ['uk', 'UK'] else x)
            height_df = pd.to_numeric(tab11_basic['身高'], errors='coerce')
            # 计算height_df的非空值计数、均值、标准差，中位数，最大值，最小值，并且将这些统计量放入一个df中名为height_sta_df
            henotnull_count = height_df.notnull().sum()
            mean = height_df.mean(skipna=True)
            std = height_df.std()
            mean_std = f"{mean:.2f}±{std:.2f}"
            height_sta_df = pd.DataFrame({'非空值计数': henotnull_count, '均值±标准差': mean_std, '中位数': height_df.median(), '最大值': height_df.max(), '最小值': height_df.min()}, index=[0])
            # 转置这个表格
            height_sta_df = height_sta_df.T
            # 列名改为“统计量”
            height_sta_df.columns = ['统计量']
            height_sta_df = height_sta_df.round(2)
            st.write("身高统计量:")
            st.write(height_sta_df)
            # 获取tab11_basic中名为“体重”的列，赋值给一个df名为weight_df
            weight_df = tab11_basic['体重']
            # 设置weight_df中的"uk","UK"为np.nan
            weight_df = weight_df.apply(lambda x: np.nan if x in ['uk', 'UK'] else x)
            weight_df = pd.to_numeric(tab11_basic['体重'], errors='coerce')
            # 计算weight_df的非空值计数、均值、标准差，中位数，最大值，最小值，并且将这些统计量放入一个df中名为weight_sta_df
            wenotnull_count = weight_df.notnull().sum()
            mean = weight_df.mean(skipna=True)
            std = weight_df.std()
            mean_std = f"{mean:.2f}±{std:.2f}"
            weight_sta_df = pd.DataFrame({'非空值计数': wenotnull_count, '均值±标准差': mean_std, '中位数': weight_df.median(), '最大值': weight_df.max(), '最小值': weight_df.min()}, index=[0])
            weight_sta_df = weight_sta_df.round(2)
            # 转置这个表格
            weight_sta_df = weight_sta_df.T
            # 列名改为“统计量”
            weight_sta_df.columns = ['统计量']
            st.write("体重统计量:")
            st.write(weight_sta_df)
            # 获取tab11_basic中名为“体表面积”的列，赋值给一个df名为bsa_df
            bsa_df = tab11_basic['体表面积']
            # 如果bsa_df中的值有”UK"，则将其替换为np.nan
            bsa_df = bsa_df.replace('UK', np.nan)
            # 计算bsa_df的非空值计数、均值、标准差，中位数，最大值，最小值，并且将这些统计量放入一个df中名为bsa_sta_df
            bsa_notnull_count = bsa_df.notnull().sum()
            bsa_df = bsa_df.astype(float)
            mean = bsa_df.mean()
            std = bsa_df.std()
            mean_std = f"{mean:.2f}±{std:.2f}"
            bsa_sta_df = pd.DataFrame({'非空值计数': bsa_notnull_count, '均值±标准差': mean_std, '中位数': bsa_df.median(), '最大值': bsa_df.max(), '最小值': bsa_df.min()}, index=[0])
            bsa_sta_df = bsa_sta_df.round(2)
            # 转置这个表格
            bsa_sta_df = bsa_sta_df.T
            # 列名改为“统计量”
            bsa_sta_df.columns = ['统计量']
            st.write("体表面积统计量:")
            st.write(bsa_sta_df)
            with pd.ExcelWriter('HN_basic.xlsx') as writer:
                    age_sta_df.to_excel(writer, sheet_name='年龄统计量')
                    sex_sta_df.to_excel(writer, sheet_name='性别统计量')
                    nation_sta_df.to_excel(writer, sheet_name='民族统计量')
                    height_sta_df.to_excel(writer, sheet_name='身高统计量')
                    weight_sta_df.to_excel(writer, sheet_name='体重统计量')
                    bsa_sta_df.to_excel(writer, sheet_name='体表面积统计量')
            st.download_button( #提供st.download_button,使用户可以下载excel到任意本地路径
                    label="点击下载",
                    data=open('HN_basic.xlsx', 'rb').read(),
                    file_name='湖南省肿瘤基线统计.xlsx',
                    mime='application/octet-stream'
                )
        else:
            st.error("请先上传文件")
            
    def tab12(self):
        st.markdown("**使用这个模块注意以下两点：**")
        st.write("1. 上传的文件是湖南省肿瘤肝癌项目的数据")
        st.write("2. 上传的文件中包含疗效评价的sheet")
        if self.file is not None:
            # 使用pd.ExeclFile()读取self.file
            tab12data = pd.ExcelFile(self.file)
            # 遍历tab12data中的sheet，将其存入一个字典中，key对应sheet名称，value对应sheet中的df
            tab12_dict = {}
            for sheet in tab12data.sheet_names:
                tab12_dict[sheet] = tab12data.parse(sheet)
            # 获取tab12_dict中key名称包含字符串”疗效评价“的sheet，赋值给一个新的dict名为eva_dict
            eva_dict = {k: v for k, v in tab12_dict.items() if '疗效评价' in k}
            for k, v in eva_dict.items():
                eva_dict[k] = v[['最佳疗效评价']]
            # 将所有的nan值替换为“不详”
            for k, v in eva_dict.items():
                eva_dict[k] = v.fillna('不详')

            # 将eva_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为eva_df
            eva_df = pd.concat(eva_dict.values(), axis=1)
            eva_df.columns = [f'访视{i+1}' for i, col in enumerate(eva_df.columns)]
            # 计算eva_df中每一列中不同值的计数（忽略空值）
            eva_count = eva_df.apply(lambda x: x.value_counts(dropna=True))
            # 计算eva_df中每一列中不同值的占比，占比=本列中某个值的计数/eva_df的行数
            eva_per = eva_count.apply(lambda x: x / len(eva_df))
            #转置eva_per和eva_count
            eva_per = eva_per.T
            eva_count = eva_count.T
            # 将计数和占比的结果交替放置到一个df中，命名为eva_sta_df
            eva_sta_df = pd.DataFrame()
            for col in eva_count.columns:
                eva_sta_df[col+'_计数'] = eva_count[col]
                eva_sta_df[col+'_占比'] = eva_per[col]
            # 将eva_sta_df中的nan值替换为0
            eva_sta_df = eva_sta_df.fillna(0)
            # 将eva_sta_df中的列名中包含字符串”占比“的列的值转换为百分数，如果值为0，则不处理
            eva_sta_df[[col for col in eva_sta_df.columns if '占比' in col]] = eva_sta_df[[col for col in eva_sta_df.columns if '占比' in col]].applymap(lambda x: f'{x:.2%}' if x != 0 else x)
            fig, ax = plt.subplots(figsize=(10, 6))
            eva_per.plot(kind='area', stacked=True, ax=ax)
            ax.set_xticks(range(len(eva_per.index)))
            ax.set_xticklabels(eva_per.index, rotation=90, fontproperties=font)
            ax.set_title('疗效评价占比面积图',fontproperties=font)
            ax.legend(prop=font)
            st.pyplot(fig)
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            eva_count.plot(kind='bar', stacked=True, ax=ax2)
            ax2.set_xticks(range(len(eva_count.index)))
            ax2.set_xticklabels(eva_count.index, rotation=90, fontproperties=font)
            ax2.set_title('疗效评价计数柱状图',fontproperties=font)
            ax2.legend(prop=font)
            st.pyplot(fig2)
            
        
            st.write("疗效评价统计:")
            st.write(eva_sta_df)
            # 将eva_sta_df保存为excel，并使用st.download_button()提供下载
            with pd.ExcelWriter('HN_eva.xlsx') as writer:
                eva_sta_df.to_excel(writer, sheet_name='疗效评价')
            st.download_button(
                    label="点击下载",
                    data=open('HN_eva.xlsx', 'rb').read(),
                    file_name='湖南省肿瘤疗效评价.xlsx',
                    mime='application/octet-stream'
                )
        else:
            st.error("请先上传文件")


    def tab13(self):
        st.markdown("**使用这个模块注意以下两点：**")
        st.write("1. 上传的文件是湖南省肿瘤肝癌项目的数据")
        st.write("2. 上传的文件中包含肿瘤诊断的sheet")
        if self.file is not None:
            # 使用pd.ExeclFile()读取self.file
            tab13data = pd.ExcelFile(self.file)
            # 遍历tab13data中的sheet，将其存入一个字典中，key对应sheet名称，value对应sheet中的df
            tab13_dict = {}
            for sheet in tab13data.sheet_names:
                tab13_dict[sheet] = tab13data.parse(sheet)
            # 获取tab13_dict中key名称包含字符串”肿瘤诊断“的sheet，赋值给一个新的dict名为diagno_dict
            diagno_dict = {k: v for k, v in tab13_dict.items() if '肿瘤诊断' in k}
            for k, v in diagno_dict.items():
                diagno_dict[k] = v[['临床诊断分期']]
            # 将所有的nan值替换为“不详”
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.fillna('不详')
            # 将所有的“-”替换为“不详”
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.replace('-', '不详')
            # 将值中所有的"期"字都去掉（只删除“期”字符串，不删除整个值）
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.replace({"期": ""}, regex=True)
            
            # 将所有的"I","II","III","IV"替换为"Ⅰ","Ⅱ","Ⅲ","Ⅳ"
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.replace({"I": "Ⅰ", "II": "Ⅱ", "III": "Ⅲ", "IV": "Ⅳ"})
            # 将所有的“一”，“二”，“三”，“四”替换为“Ⅰ”，“Ⅱ”，“Ⅲ”，“Ⅳ”
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.replace({"一": "Ⅰ", "二": "Ⅱ", "三": "Ⅲ", "四": "Ⅳ"})
            # 将所有的“A”，“B”，“C”，“D”替换为“Ⅰ”，“Ⅱ”，“Ⅲ”，“Ⅳ”
            for k, v in diagno_dict.items():
                diagno_dict[k] = v.replace({"A": "Ⅰ", "B": "Ⅱ", "C": "Ⅲ", "D": "Ⅳ"})
            # 将diagno_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为diagno_df
            diagno_df = pd.concat(diagno_dict.values(), axis=1)
            diagno_df.columns = [f'访视{i+1}' for i, col in enumerate(diagno_df.columns)]
            # 计算diagno_df中每一列中不同值的计数（忽略空值）
            diagno_count = diagno_df.apply(lambda x: x.value_counts(dropna=True))
            # 计算diagno_df中每一列中不同值的占比，占比=本列中某个值的计数/diagno_df的行数
            diagno_per = diagno_count.apply(lambda x: x / len(diagno_df))
            #转置diagno_per和diagno_count
            diagno_per = diagno_per.T
            diagno_count = diagno_count.T
            # 重新排列diagno_per和diagno_count的列的顺序，按照“0期”，“Ⅰ期”，“Ⅱ期”，“Ⅲ期”，“Ⅳ期”的顺序，将”不详“放在最后
            #diagno_per = diagno_per[['0期', 'I期', 'II期', 'III期', 'IV期', '不详']]
            #diagno_count = diagno_count[['0期', 'I期', 'II期', 'III期', 'IV期', '不详']]

            # 将计数和占比的结果交替放置到一个df中，命名为diagno_sta_df
            diagno_sta_df = pd.DataFrame()
            for col in diagno_count.columns:
                diagno_sta_df[col+'_计数'] = diagno_count[col]
                diagno_sta_df[col+'_占比'] = diagno_per[col]
            # 将diagno_sta_df中的nan值替换为0
            diagno_sta_df = diagno_sta_df.fillna(0)
            # 将diagno_sta_df中的列名中包含字符串”占比“的列的值转换为百分数，如果值为0，则不处理
            diagno_sta_df[[col for col in diagno_sta_df.columns if '占比' in col]] = diagno_sta_df[[col for col in diagno_sta_df.columns if '占比' in col]].applymap(lambda x: f'{x:.2%}' if x != 0 else x)

            fig, ax = plt.subplots(figsize=(10, 6))
            diagno_per.plot(kind='area', stacked=True, ax=ax)
            ax.set_xticks(range(len(diagno_per.index)))
            ax.set_xticklabels(diagno_per.index, rotation=90, fontproperties=font)
            ax.set_title('肿瘤诊断占比面积图',fontproperties=font)
            ax.legend(prop=font)
            st.pyplot(fig)

            fig2, ax2 = plt.subplots(figsize=(10, 6))
            diagno_count.plot(kind='bar', stacked=True, ax=ax2)
            ax2.set_xticks(range(len(diagno_count.index)))
            ax2.set_xticklabels(diagno_count.index, rotation=90, fontproperties=font)
            ax2.set_title('肿瘤诊断计数柱状图',fontproperties=font)
            ax2.legend(prop=font)
            st.pyplot(fig2)

            
            
            
            st.write("肿瘤诊断统计:")
            st.write(diagno_sta_df)
            # 将diagno_sta_df保存为excel，并使用st.download_button()提供下载
            with pd.ExcelWriter('HN_diagno.xlsx') as writer:
                diagno_sta_df.to_excel(writer, sheet_name='肿瘤诊断')
            st.download_button(
                    label="点击下载",
                    data=open('HN_diagno.xlsx', 'rb').read(),
                    file_name='湖南省肿瘤诊断.xlsx',
                    mime='application/octet-stream'
                )
        else:
            st.error("请先上传文件")

    def tab14(self):
        st.markdown("**使用这个模块注意以下两点：**")
        st.write("1. 上传的文件是湖南省肿瘤肝癌项目的数据")
        st.write("2. 上传的文件中包含血常规的sheet")
        st.warning('出图后大概看一下没问题就麻溜拖到最后先把图下载到本地，这个模块很容易内存溢出导致自动刷新，一刷新就啥都没了。待我跟雪梅老师沟通一下服务器的事情。')
        if self.file is not None:
            tab14data = pd.ExcelFile(self.file)
            tab14_dict = {}
            for sheet in tab14data.sheet_names:
                tab14_dict[sheet] = tab14data.parse(sheet)
            # 获取tab14_dict中key名称包含字符串”血常规“的sheet，赋值给一个新的dict名为blood_dict
            blood_dict = {k: v for k, v in tab14_dict.items() if '血常规' in k}
            # 获取blood_dict中的df中的“白细胞”列，赋值给一个新的dict名为wbc_dict
            wbc_dict = {k: v[['白细胞']] for k, v in blood_dict.items()}
            # 将wbc_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为wbc_df
            wbc_df = pd.concat(wbc_dict.values(), axis=1)
            wbc_df.columns = [f'访视{i+1}' for i, col in enumerate(wbc_df.columns)]
            # 使用箱型图表示wbc_df中每一列数据，将所有箱放入同一个坐标轴，x轴为wbc_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig1, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=wbc_df, ax=ax)
            ax.set_xticklabels(wbc_df.columns, rotation=45, ha='right',fontproperties=font)
            
            ax.set_title('访视期间白细胞计数变化情况',fontproperties=font)
            st.pyplot(fig1)

            # 获取blood_dict中的df中的“中性粒细胞百分比”列，赋值给一个新的dict名为neut_dict
            neut_dict = {k: v[['中性粒细胞百分比']] for k, v in blood_dict.items()}
            # 将neut_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为neut_df
            neut_df = pd.concat(neut_dict.values(), axis=1)
            neut_df.columns = [f'访视{i+1}' for i, col in enumerate(neut_df.columns)]
            # 使用箱型图表示neut_df中每一列数据，将所有箱放入同一个坐标轴，x轴为neut_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig2, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=neut_df, ax=ax)
            ax.set_xticklabels(neut_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间中性粒细胞百分比变化情况',fontproperties=font)
            st.pyplot(fig2)

            # 获取blood_dict中的df中的“淋巴细胞百分比”列，赋值给一个新的dict名为lymph_dict
            lymph_dict = {k: v[['淋巴细胞百分比']] for k, v in blood_dict.items()}
            # 将lymph_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为lymph_df
            lymph_df = pd.concat(lymph_dict.values(), axis=1)
            lymph_df.columns = [f'访视{i+1}' for i, col in enumerate(lymph_df.columns)]
            # 使用箱型图表示lymph_df中每一列数据，将所有箱放入同一个坐标轴，x轴为lymph_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig3, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=lymph_df, ax=ax)
            ax.set_xticklabels(lymph_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间淋巴细胞百分比变化情况',fontproperties=font)
            st.pyplot(fig3)

            # 获取blood_dict中的df中的“单核细胞百分比”列，赋值给一个新的dict名为mono_dict
            mono_dict = {k: v[['单核细胞百分比']] for k, v in blood_dict.items()}
            # 将mono_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mono_df
            mono_df = pd.concat(mono_dict.values(), axis=1)
            mono_df.columns = [f'访视{i+1}' for i, col in enumerate(mono_df.columns)]
            # 使用箱型图表示mono_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mono_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig4, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mono_df, ax=ax)
            ax.set_xticklabels(mono_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间单核细胞百分比变化情况',fontproperties=font)
            st.pyplot(fig4)

            # 获取blood_dict中"嗜酸性粒细胞百分比"列，赋值给一个新的dict名为eos_dict
            eos_dict = {k: v[['嗜酸性粒细胞百分比']] for k, v in blood_dict.items()}
            # 将eos_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为eos_df
            eos_df = pd.concat(eos_dict.values(), axis=1)
            eos_df.columns = [f'访视{i+1}' for i, col in enumerate(eos_df.columns)]
            # 使用箱型图表示eos_df中每一列数据，将所有箱放入同一个坐标轴，x轴为eos_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig5, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=eos_df, ax=ax)
            ax.set_xticklabels(eos_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间嗜酸性粒细胞百分比变化情况',fontproperties=font)
            st.pyplot(fig5)

            # 获取blood_dict中"嗜碱性粒细胞百分比"列，赋值给一个新的dict名为baso_dict
            baso_dict = {k: v[['嗜碱性粒细胞百分比']] for k, v in blood_dict.items()}
            # 将baso_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为baso_df
            baso_df = pd.concat(baso_dict.values(), axis=1)
            baso_df.columns = [f'访视{i+1}' for i, col in enumerate(baso_df.columns)]
            # 使用箱型图表示baso_df中每一列数据，将所有箱放入同一个坐标轴，x轴为baso_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig6, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=baso_df, ax=ax)
            ax.set_xticklabels(baso_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间嗜碱性粒细胞百分比变化情况',fontproperties=font)
            st.pyplot(fig6)

            # 获取blood_dict中"中性粒细胞绝对值"列，赋值给一个新的dict名为neutabs_dict
            neutabs_dict = {k: v[['中性粒细胞绝对值']] for k, v in blood_dict.items()}
            # 将neut_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为neut_df
            neutabs_df = pd.concat(neutabs_dict.values(), axis=1)
            neutabs_df.columns = [f'访视{i+1}' for i, col in enumerate(neutabs_df.columns)]
            # 使用箱型图表示neut_df中每一列数据，将所有箱放入同一个坐标轴，x轴为neut_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig7, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=neutabs_df, ax=ax)
            ax.set_xticklabels(neutabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间中性粒细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig7)

            # 获取blood_dict中"淋巴细胞绝对值"列，赋值给一个新的dict名为lymphabs_dict
            lymphabs_dict = {k: v[['淋巴细胞绝对值']] for k, v in blood_dict.items()}
            # 将lymphabs_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为lymphabs_df
            lymphabs_df = pd.concat(lymphabs_dict.values(), axis=1)
            lymphabs_df.columns = [f'访视{i+1}' for i, col in enumerate(lymphabs_df.columns)]
            # 使用箱型图表示lymphabs_df中每一列数据，将所有箱放入同一个坐标轴，x轴为lymphabs_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig8, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=lymphabs_df, ax=ax)
            ax.set_xticklabels(lymphabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间淋巴细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig8)

            # 获取blood_dict中"单核细胞绝对值"列，赋值给一个新的dict名为monoabs_dict
            monoabs_dict = {k: v[['单核细胞绝对值']] for k, v in blood_dict.items()}
            # 将monoabs_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为monoabs_df
            monoabs_df = pd.concat(monoabs_dict.values(), axis=1)
            monoabs_df.columns = [f'访视{i+1}' for i, col in enumerate(monoabs_df.columns)]
            # 使用箱型图表示monoabs_df中每一列数据，将所有箱放入同一个坐标轴，x轴为monoabs_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig9, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=monoabs_df, ax=ax)
            ax.set_xticklabels(monoabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间单核细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig9)

            # 获取blood_dict中"嗜酸性粒细胞绝对值"列，赋值给一个新的dict名为eosabs_dict
            eosabs_dict = {k: v[['嗜酸性粒细胞绝对值']] for k, v in blood_dict.items()}
            # 将eosabs_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为eosabs_df
            eosabs_df = pd.concat(eosabs_dict.values(), axis=1)
            eosabs_df.columns = [f'访视{i+1}' for i, col in enumerate(eosabs_df.columns)]
            # 使用箱型图表示eosabs_df中每一列数据，将所有箱放入同一个坐标轴，x轴为eosabs_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig10, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=eosabs_df, ax=ax)
            ax.set_xticklabels(eosabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间嗜酸性粒细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig10)

            # 获取blood_dict中"嗜碱性粒细胞绝对值"列，赋值给一个新的dict名为basabs_dict
            basabs_dict = {k: v[['嗜碱性粒细胞绝对值']] for k, v in blood_dict.items()}
            # 将basabs_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为basabs_df
            basabs_df = pd.concat(basabs_dict.values(), axis=1)
            basabs_df.columns = [f'访视{i+1}' for i, col in enumerate(basabs_df.columns)]
            # 使用箱型图表示basabs_df中每一列数据，将所有箱放入同一个坐标轴，x轴为basabs_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig11, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=basabs_df, ax=ax)
            ax.set_xticklabels(basabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间嗜碱性粒细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig11)

            # 获取blood_dict中"红细胞"列，赋值给一个新的dict名为neuabs_dict
            neuabs_dict = {k: v[['红细胞']] for k, v in blood_dict.items()}
            # 将neuabs_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为neuabs_df
            neuabs_df = pd.concat(neuabs_dict.values(), axis=1)
            neuabs_df.columns = [f'访视{i+1}' for i, col in enumerate(neuabs_df.columns)]
            # 使用箱型图表示neuabs_df中每一列数据，将所有箱放入同一个坐标轴，x轴为neuabs_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig12, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=neuabs_df, ax=ax)
            ax.set_xticklabels(neuabs_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间红细胞绝对值变化情况',fontproperties=font)
            st.pyplot(fig12)

            # 获取blood_dict中"血红蛋白"列，赋值给一个新的dict名为hgb_dict
            hgb_dict = {k: v[['血红蛋白']] for k, v in blood_dict.items()}
            # 将hgb_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为hgb_df
            hgb_df = pd.concat(hgb_dict.values(), axis=1)
            hgb_df.columns = [f'访视{i+1}' for i, col in enumerate(hgb_df.columns)]
            # 使用箱型图表示hgb_df中每一列数据，将所有箱放入同一个坐标轴，x轴为hgb_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig13, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=hgb_df, ax=ax)
            ax.set_xticklabels(hgb_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间血红蛋白变化情况',fontproperties=font)
            st.pyplot(fig13)

            # 获取blood_dict中"红细胞压积"列，赋值给一个新的dict名为plt_dict
            plt_dict = {k: v[['红细胞压积']] for k, v in blood_dict.items()}
            # 将plt_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为plt_df
            plt_df = pd.concat(plt_dict.values(), axis=1)
            plt_df.columns = [f'访视{i+1}' for i, col in enumerate(plt_df.columns)]
            # 使用箱型图表示plt_df中每一列数据，将所有箱放入同一个坐标轴，x轴为plt_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig14, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=plt_df, ax=ax)
            ax.set_xticklabels(plt_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间红细胞压积变化情况',fontproperties=font)
            st.pyplot(fig14)

            # 获取blood_dict中"平均红细胞体积"列，赋值给一个新的dict名为mcv_dict
            mcv_dict = {k: v[['平均红细胞体积']] for k, v in blood_dict.items()}
            # 将mcv_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mcv_df
            mcv_df = pd.concat(mcv_dict.values(), axis=1)
            mcv_df.columns = [f'访视{i+1}' for i, col in enumerate(mcv_df.columns)]
            # 使用箱型图表示mcv_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mcv_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig15, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mcv_df, ax=ax)
            ax.set_xticklabels(mcv_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间平均红细胞体积变化情况',fontproperties=font)
            st.pyplot(fig15)

            # 获取blood_dict中"平均RBC血红蛋白含量"列，赋值给一个新的dict名为mch_dict
            mch_dict = {k: v[['平均RBC血红蛋白含量']] for k, v in blood_dict.items()}
            # 将mch_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mch_df
            mch_df = pd.concat(mch_dict.values(), axis=1)
            mch_df.columns = [f'访视{i+1}' for i, col in enumerate(mch_df.columns)]
            # 使用箱型图表示mch_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mch_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig16, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mch_df, ax=ax)
            ax.set_xticklabels(mch_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间平均RBC血红蛋白含量变化情况',fontproperties=font)
            st.pyplot(fig16)

            # 获取blood_dict中"平均RBC血红蛋白浓度"列，赋值给一个新的dict名为mchc_dict
            mchc_dict = {k: v[['平均RBC血红蛋白浓度']] for k, v in blood_dict.items()}
            # 将mchc_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mchc_df
            mchc_df = pd.concat(mchc_dict.values(), axis=1)
            mchc_df.columns = [f'访视{i+1}' for i, col in enumerate(mchc_df.columns)]
            # 使用箱型图表示mchc_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mchc_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig17, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mchc_df, ax=ax)
            ax.set_xticklabels(mchc_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间平均RBC血红蛋白浓度变化情况',fontproperties=font)
            st.pyplot(fig17)

            # 获取blood_dict中"红细胞分布密度CV值"列，赋值给一个新的dict名为rdw_dict
            rdw_dict = {k: v[['红细胞分布密度CV值']] for k, v in blood_dict.items()}
            # 将rdw_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为rdw_df
            rdw_df = pd.concat(rdw_dict.values(), axis=1)
            rdw_df.columns = [f'访视{i+1}' for i, col in enumerate(rdw_df.columns)]
            # 使用箱型图表示rdw_df中每一列数据，将所有箱放入同一个坐标轴，x轴为rdw_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig18, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=rdw_df, ax=ax)
            ax.set_xticklabels(rdw_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间红细胞分布密度CV值变化情况',fontproperties=font)
            st.pyplot(fig18)

            # 获取blood_dict中"红细胞分布密度SD值"列，赋值给一个新的dict名为mpv_dict
            mpv_dict = {k: v[['红细胞分布密度SD值']] for k, v in blood_dict.items()}
            # 将mpv_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mpv_df
            mpv_df = pd.concat(mpv_dict.values(), axis=1)
            mpv_df.columns = [f'访视{i+1}' for i, col in enumerate(mpv_df.columns)]
            # 使用箱型图表示mpv_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mpv_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig19, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mpv_df, ax=ax)
            ax.set_xticklabels(mpv_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间红细胞分布密度SD值变化情况',fontproperties=font)
            st.pyplot(fig19)

            # 获取blood_dict中"血小板计数"列，赋值给一个新的dict名为plt_dict
            plt_dict = {k: v[['血小板']] for k, v in blood_dict.items()}
            # 将plt_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为plt_df
            plt_df = pd.concat(plt_dict.values(), axis=1)
            plt_df.columns = [f'访视{i+1}' for i, col in enumerate(plt_df.columns)]
            # 使用箱型图表示plt_df中每一列数据，将所有箱放入同一个坐标轴，x轴为plt_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig20, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=plt_df, ax=ax)
            ax.set_xticklabels(plt_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间血小板计数变化情况',fontproperties=font)
            st.pyplot(fig20)

            # 获取blood_dict中"血小板比积"列，赋值给一个新的dict名为mpv_dict
            mpv_dict = {k: v[['血小板比积']] for k, v in blood_dict.items()}
            # 将mpv_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mpv_df
            mpv_df = pd.concat(mpv_dict.values(), axis=1)
            mpv_df.columns = [f'访视{i+1}' for i, col in enumerate(mpv_df.columns)]
            # 使用箱型图表示mpv_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mpv_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig21, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mpv_df, ax=ax)
            ax.set_xticklabels(mpv_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间血小板比积变化情况',fontproperties=font)
            st.pyplot(fig21)

            # 获取blood_dict中"血小板平均体积"列，赋值给一个新的dict名为mpv_dict
            mpv_dict = {k: v[['血小板平均体积']] for k, v in blood_dict.items()}
            # 将mpv_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mpv_df
            mpv_df = pd.concat(mpv_dict.values(), axis=1)
            mpv_df.columns = [f'访视{i+1}' for i, col in enumerate(mpv_df.columns)]
            # 使用箱型图表示mpv_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mpv_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig22, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mpv_df, ax=ax)
            ax.set_xticklabels(mpv_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间血小板平均体积变化情况',fontproperties=font)  
            st.pyplot(fig22)

            # 获取blood_dict中"血小板分布宽度"列，赋值给一个新的dict名为mpvkd_dict
            mpvkd_dict = {k: v[['血小板分布宽度']] for k, v in blood_dict.items()}
            # 将mpvkd_dict中的df合并为一个df，并且按照顺序在合并后的列名前加上“访视[i]”，名为mpvkd_df
            mpvkd_df = pd.concat(mpvkd_dict.values(), axis=1)
            mpvkd_df.columns = [f'访视{i+1}' for i, col in enumerate(mpvkd_df.columns)]
            # 使用箱型图表示mpvkd_df中每一列数据，将所有箱放入同一个坐标轴，x轴为mpvkd_df的列名，y轴为数值，最后使用st.pyplot展示该图
            fig23, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=mpvkd_df, ax=ax)
            ax.set_xticklabels(mpvkd_df.columns, rotation=45, ha='right',fontproperties=font)
            ax.set_title('访视期间血小板分布宽度变化情况',fontproperties=font)
            st.pyplot(fig23)

            # 将fig1，fig2，fig3，fig4保存为图片文件
            fig1.savefig('白细胞计数.png')
            fig2.savefig('中性粒细胞百分比.png')
            fig3.savefig('淋巴细胞百分比.png')
            fig4.savefig('单核细胞百分比.png')
            fig5.savefig('嗜酸性粒细胞百分比.png')
            fig6.savefig('嗜碱性粒细胞百分比.png')
            fig7.savefig('中性粒细胞绝对值.png')
            fig8.savefig('淋巴细胞绝对值.png')
            fig9.savefig('单核细胞绝对值.png')
            fig10.savefig('嗜酸性粒细胞绝对值.png')
            fig11.savefig('嗜碱性粒细胞绝对值.png')
            fig12.savefig('红细胞.png')
            fig13.savefig('血红蛋白.png')
            fig14.savefig('红细胞压积.png')
            fig15.savefig('平均红细胞体积.png')
            fig16.savefig('平均RBC血红蛋白含量.png')
            fig17.savefig('平均RBC血红蛋白浓度.png')
            fig18.savefig('红细胞分布密度CV值.png')
            fig19.savefig('红细胞分布密度SD值.png')
            fig20.savefig('血小板.png')
            fig21.savefig('血小板比积.png')
            fig22.savefig('血小板平均体积.png')
            fig23.savefig('血小板分布宽度.png')

            # 将这些图片文件写入一个压缩文件
            with zipfile.ZipFile('figures.zip', 'w') as zipf:
                zipf.write('白细胞计数.png')
                zipf.write('中性粒细胞百分比.png')
                zipf.write('淋巴细胞百分比.png')
                zipf.write('单核细胞百分比.png')
                zipf.write('嗜酸性粒细胞百分比.png')
                zipf.write('嗜碱性粒细胞百分比.png')
                zipf.write('中性粒细胞绝对值.png')
                zipf.write('淋巴细胞绝对值.png')
                zipf.write('单核细胞绝对值.png')
                zipf.write('嗜酸性粒细胞绝对值.png')
                zipf.write('嗜碱性粒细胞绝对值.png')
                zipf.write('红细胞.png')
                zipf.write('血红蛋白.png')
                zipf.write('红细胞压积.png')
                zipf.write('平均红细胞体积.png')
                zipf.write('平均RBC血红蛋白含量.png')
                zipf.write('平均RBC血红蛋白浓度.png')
                zipf.write('红细胞分布密度CV值.png')
                zipf.write('红细胞分布密度SD值.png')
                zipf.write('血小板.png')
                zipf.write('血小板比积.png')
                zipf.write('血小板平均体积.png')
                zipf.write('血小板分布宽度.png')

            # 使用st.download_button下载这个压缩文件
            st.download_button(
                label="点击下载",
                data=open('figures.zip', 'rb').read(),
                file_name='figures.zip',
                mime='application/zip'
            )
        else:
            st.error('请上传文件')
            
            
    def tab15(self):
        
        st.title('中介效应与调节效应计算')
        
        # 给出一个上传文件的按钮，label是”上传用于中介/调节效应分析的数据“，type是"csv"或"xlsx"，key是”mediation“
        medfile = st.file_uploader(label='上传用于中介/调节效应分析的数据', type=['xlsx'], key='mediation')
        if medfile is not None:
            medfile = pd.read_excel(medfile)
            # 放置一个st.radio, label是”选择中介/调节效应分析的方法“，options是一个列表，内容为”中介效应“和”调节效应“，key是”mediation_method“
            med_method = st.radio(label='选择中介/调节效应分析的方法', options=['中介效应', '调节效应'], key='mediation_method')
            # 放置一个st.multiselect, label是”选择自变量“，options是一个列表，内容为medfile中所有的列名，key是”mediation_independent“
            med_independent = st.multiselect(label='选择自变量', options=medfile.columns, key='mediation_independent')
            # 放置一个st.selectbox, label是”选择因变量“，options是一个列表，内容为medfile中所有的列名，key是”mediation_dependent“
            med_dependent = st.selectbox(label='选择因变量', options=medfile.columns, key='mediation_dependent')
            # 放置一个st.selectbox, label是”选择中介变量“，options是一个列表，内容为medfile中所有的列名，key是”mediation_mediator“
            med_mediator = st.selectbox(label='选择中介变量', options=medfile.columns, key='mediation_mediator')
            # 放置一个radio，label是“选择中介变量类型”，options是一个列表，内容为“连续变量”和“分类变量”，key是“mediation_mediator_type”
            med_mediator_type = st.radio(label='选择中介变量类型', options=['连续变量', '分类变量'], key='mediation_mediator_type')
            # 放置一个st.button, label是”开始分析“，key是”mediation_analysis“
            if st.button(label='开始分析', key='mediation_analysis'):
                if med_method == '中介效应':
                    if med_mediator_type == '连续变量':
                        # X是medfile中的med_independent列，输出的结果是一个DataFrame
                        X = medfile[med_independent]
                        # M是medfile中的med_mediator列，输出的结果是一个DataFrame
                        M = medfile[med_mediator]
                        # Y是medfile中的med_dependent列，输出的结果是一个DataFrame
                        Y = medfile[med_dependent]
                        # 拟合中介回归模型,使用sm.OLS
                        model_mediator = sm.OLS(Y, sm.add_constant(X)).fit()
                        # 计算中介效应
                        indirect_effect = model_mediator.params[1] * M.mean()
                        # 计算总效应
                        total_effect = model_mediator.params[1] * M.mean() + model_mediator.params[2]
                        # 输出中介效应和总效应，使用st.dataframe
                        st.dataframe(pd.DataFrame({'中介效应': [indirect_effect], '总效应': [total_effect]}))
                        # 画图，使用st.pyplot
                        fig1, ax = plt.subplots()
                        sns.regplot(x=M, y=Y, x_ci=None, scatter_kws={"color": "black"}, line_kws={"color": "red"})
                        # 设置x轴标签(中文，fontproperties=font)
                        plt.xlabel('中介变量', fontproperties=font)
                        # 设置y轴标签(中文，fontproperties=font)
                        plt.ylabel('因变量', fontproperties=font)
                        # 设置图标题(中文，fontproperties=font)
                        plt.title('中介效应', fontproperties=font)
                        
                        # 显示图像
                        st.pyplot(fig1)

                        # 
                    else:
                        # X是medfile中的med_independent列，输出的结果是一个DataFrame
                        X = medfile[med_independent]
                        # M是medfile中的med_mediator列，输出的结果是一个DataFrame
                        M = medfile[med_mediator]
                        # Y是medfile中的med_dependent列，输出的结果是一个DataFrame
                        Y = medfile[med_dependent]
                        # 构建logistic回归模型，中介变量为分类变量
                        # Step 1: 预测中介变量 M。由于M是二分类变量，我们使用逻辑回归
                        logit_model = smf.logit('M ~ X', data=medfile).fit()
                        medfile['PreM'] = logit_model.predict(medfile)
                        # Step 2: 使用预测得到的 M 和 X 预测 Y，这里我们使用线性回归
                        mediation_model = smf.ols(f'Y ~ PreM + {" + ".join(med_independent)}', data=medfile).fit()
                        coeff_X = mediation_model.params[med_independent]
                        coeff_predicted_M = mediation_model.params['PreM']                                        
                        # 输出所有结果和参数，使用st.write
                        st.write(mediation_model.summary())
                        # 输出中介效应和总效应，使用st.dataframe
                        st.dataframe(pd.DataFrame({'中介效应': [coeff_X * coeff_predicted_M], '总效应': [coeff_X * coeff_predicted_M + mediation_model.params["PreM"]]}))

                        # 创建路径图
                        fig, ax = plt.subplots(figsize=(10, 5))
                        # 绘制变量
                        ax.text(0.2, 0.6, 'X', fontsize=12)
                        for i in range(len(med_independent)):
                            ax.text(0.2+(i+1)*0.2, 0.6, f'X{i+1}', fontsize=12)
                        ax.text(0.4, 0.4, 'PreM', fontsize=12)
                        ax.text(0.7, 0.6, 'Y', fontsize=12)
                        # 绘制路径
                        ax.annotate('', xy=(0.35, 0.6), xytext=(0.25, 0.6), arrowprops=dict(arrowstyle='->'))
                        for i in range(len(med_independent)):
                            ax.annotate('', xy=(0.2+(i+1)*0.2, 0.6), xytext=(0.25, 0.6), xycoords='data', textcoords='data', 
                                arrowprops=dict(arrowstyle='->', linestyle='dashed'))
                        ax.annotate('', xy=(0.65, 0.6), xytext=(0.45, 0.6), arrowprops=dict(arrowstyle='->'))
                        ax.annotate('', xy=(0.65, 0.6), xytext=(0.25, 0.6), xycoords='data', textcoords='data', 
                            arrowprops=dict(arrowstyle='->', linestyle='dashed'))
                        # 添加系数
                        ax.text(0.3, 0.65, f'{coeff_X[0]:.2f}', fontsize=10)
                        for i in range(len(med_independent)-1):
                            ax.text(0.2+(i+1)*0.2, 0.65, f'{coeff_X[i+1]:.2f}', fontsize=10)
                        ax.text(0.5, 0.65, f'{coeff_predicted_M:.2f}', fontsize=10)
                        # 删除坐标轴
                        ax.axis('off')
                        # 添加标题
                        plt.title('中介效应路径图', fontproperties=font)
                        
                        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                        st.pyplot(fig)



                



                        

                    

            
            
            


if __name__ == "__main__":
    app = MyApp()
    app.run()

