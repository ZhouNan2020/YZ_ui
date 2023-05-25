

import streamlit as st
import pandas as pd
import numpy as np
import re



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

        tabs = ["数据预览", "按索引筛选", "复杂分组",'划分试验组','多试验组的计数统计']
        st.sidebar.title("导航")
        selected_tab = st.sidebar.radio("选择一个标签页", tabs)

        if selected_tab == "数据预览":
            self.tab1()
        elif selected_tab =="按索引筛选":
            self.tab2()
        elif selected_tab ==  "复杂分组":
            self.tab3()
        elif selected_tab ==  '划分试验组':
            self.tab4()
        elif selected_tab == '多试验组的计数统计':
            self.tab5()

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
                        df_new[col] = [non_null_count, round(mean,2),mean_plus_std, round(median,2), round(max_val,2), round(min_val,2)] #将当前列的统计结果添加到df_new中
                    df_new["sheet"] = sheet #添加一个名为“sheet”的列，值为当前sheet的名称
                    df_new["统计值"] = ["非空值计数", "平均值", "平均值±标准差", "中位数", "最大值", "最小值"] #添加一个名为“统计值”的列，值为统计结果的名称
                    df_new = df_new[["统计值"] + list(df_new.columns[:-1])] #调整列的顺序
                    df_new = df_new.set_index('sheet') #将“sheet”列设置为索引
                    self.tab3df_list.append(df_new) #将当前sheet的统计结果添加到df_list中
                else: #如果self.col_selected中的所有列名不都在self.sheetdict[sheet]的列名中
                    continue #跳过当前循环，执行下一个循环
            self.df_final = pd.concat(self.tab3df_list, axis=0) #将df_list中的所有dataframe合并成一个dataframe
            st.dataframe(self.df_final) #在页面上显示合并后的dataframe
            st.download_button(
                label="下载结果",
                data=self.df_final.to_csv(index=False).encode(),
                file_name="finaldata.csv",
                mime="text/csv"
            )

        
        
    
    

   



    def tab4(self):
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
                    #如果self.sheetdict的key对应的dataframe中有列名为groupcol的列，则按照groupcol进行分组
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
        if self.file is not None: #如果self.file不为空
            self.tab5raw_data = pd.ExcelFile(self.file)
            self.combinedata = pd.concat([self.tab5raw_data.parse(sheet_name) for sheet_name in self.tab5raw_data.sheet_names], axis=1, join='inner')
            self.combinedata = self.combinedata.loc[:,~self.combinedata.columns.duplicated()] 
            self.combinedata = self.combinedata.fillna("未知")
            st.write(self.combinedata)
            st.markdown("**请选择作为分组依据的列**") #在页面上显示文本
            self.tab5selectcol = st.selectbox("选择列", self.combinedata.columns, key="tab5selectcol") #提供一个下拉单选框，标签为“请选择作为分组依据的列”备选项是self.combinedata中的所有列，选择结果赋值给self.tab5selectcol
            st.markdown("**请选择需要进行描述性统计的列**") #在页面上显示文本
            self.tab5stacol = st.selectbox("选择列", self.combinedata.columns, key="tab5stacol") #提供第二个下拉单选框，标签为“请选择需要进行描述性统计的列”，赋值给self.tab5stacol
            self.combinedata[self.tab5selectcol] = self.combinedata[self.tab5selectcol].fillna("未知")
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
                    for key in sta_dict.keys():
                        st.write(key)

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
                    for key in self.tab5groupdict.keys():
                        cate_df = self.tab5groupdict[key]
                        st.write(cate_df[self.tab5stacol])
                        cate_df[self.tab5stacol].fillna('未知', limit=cate_df.shape[0]-1, inplace=True) #将cate_df中空值使用‘未知’替代，限制为cate_df的总行数，即不填充尾行之后的值
                        cate_df_count = cate_df[self.tab5stacol].value_counts(dropna=True)
                        cate_df_percent = cate_df[self.tab5stacol].value_counts(normalize=True, dropna=True)
                        cate_df_percent = cate_df_percent.round(2) #保留2位小数
                        cate_count_df = pd.concat([cate_df_count, cate_df_percent], axis=1)
                        cate_count_df.columns = ['例数', '占比']
                        cate_count_df.loc['合计'] = cate_count_df.sum()
                        cate_dict[key] = cate_count_df
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
            if st.button('额外统计：对年龄进行分层计数'):    
    
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
                        #else:
                            #return '未知'

                age_dict = {}
                for key in self.tab5groupdict.keys():
                    df = self.tab5groupdict[key]
                    df['年龄_AGE'] = df['年龄_AGE'].apply(age_group)
                    age_count = df['年龄_AGE'].value_counts()
                    age_percent = df['年龄_AGE'].value_counts(normalize=True)
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

                    

 

        


        
        

        

        


if __name__ == "__main__":
    app = MyApp()
    app.run()
