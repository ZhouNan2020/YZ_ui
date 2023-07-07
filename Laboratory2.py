import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from scipy import stats
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test
#%%
font = font_manager.FontProperties(fname='simhei.ttf')

parameters = {'xtick.labelsize': 20,
              'ytick.labelsize': 20,
              
              'axes.unicode_minus':False}
plt.rcParams.update(parameters)
#%%
# 在st.sidebar中添加一个按钮，用于上传xlsx的文件
file = st.sidebar.file_uploader("上传xlsx文件", type="xlsx")
if file is not None:
    tab16data = pd.ExcelFile(file)
    tab16_dict = {}
    for sheet in tab16data.sheet_names:
        tab16_dict[sheet] = tab16data.parse(sheet)
    # 为tab16data中每一个sheet添加一个label列，默认值为nan
    for sheet in tab16data.sheet_names:
        tab16_dict[sheet]['label'] = np.nan
    # 读取match.xlsx
    match = pd.read_excel('match.xlsx')
    # 遍历tab16_dict中的每一个df，并将其中每一个df的”subject_id“与match中的“index”进行比较，如果match中的”index“列的值不存在与tab16_dict中df的”subject_id“列中，则将match中的”index“列的值添加到tab16_dict中df的”subject_id“列中，对应行中其他列的值为nan
    # 遍历tab16_dict中的每一个df
    for sheet in tab16_dict.keys():
        # 获取当前df的"subject_id"列的值
        subject_ids = tab16_dict[sheet]['subject_id'].values
        # 获取match中"index"列的值
        match_indexes = match['index'].values
        # 找出match中"index"列的值中不存在于当前df的"subject_id"列的值
        new_indexes = [index for index in match_indexes if index not in subject_ids]
        # 将这些新的index添加到当前df的"subject_id"列中，对应行中其他列的值为nan
        for new_index in new_indexes:
            new_row = pd.Series([new_index] + [np.nan]*(len(tab16_dict[sheet].columns)-1), index=tab16_dict[sheet].columns)
            tab16_dict[sheet] = pd.concat([tab16_dict[sheet], pd.DataFrame(new_row).T])
    # 读取DLC_test.xlsx
    dlct = pd.read_excel('DLC_test.xlsx')
    # 读取DLC_control.xlsx
    dlcc = pd.read_excel('DLC_control.xlsx')
    # 读取DLC_unmatch.xlsx
    dlcu = pd.read_excel('DLC_unmatch.xlsx')
    # 遍历tab16_dict中的每一个key，如果其中的subject_id列的值出现在dlcu的index列中，则删除tab16_dict中该subject_id对应的行的数据
    for sheet in tab16data.sheet_names:
        if tab16_dict[sheet]['subject_id'].isin(dlcu['index']).any():
            tab16_dict[sheet].drop(tab16_dict[sheet][tab16_dict[sheet]['subject_id'].isin(dlcu['index'])].index, inplace=True)
    # 遍历tab16_dict中的每一个key，如果其中的subject_id列的值出现在dlct的index列中，则在tab16_dict中该subject_id对应的行的label列中填入"试验组"
    for sheet in tab16data.sheet_names:
        if tab16_dict[sheet]['subject_id'].isin(dlct['index']).any():
            tab16_dict[sheet].loc[tab16_dict[sheet]['subject_id'].isin(dlct['index']), 'label'] = '试验组'
    # 遍历tab16_dict中的每一个key，如果其中的subject_id列的值出现在dlcc的index列中，则在tab16_dict中该subject_id对应的行的label列中填入"对照组"
    for sheet in tab16data.sheet_names:
        if tab16_dict[sheet]['subject_id'].isin(dlcc['index']).any():
            tab16_dict[sheet].loc[tab16_dict[sheet]['subject_id'].isin(dlcc['index']), 'label'] = '对照组'



    # 从tab16_dict中提取出所有key名包含”#尿常规“的df，形成一个新的dict
    tab16_dict_urine = {}
    for sheet in tab16_dict.keys():
        if '#尿常规' in sheet:
            tab16_dict_urine[sheet] = tab16_dict[sheet]
    # 遍历tab16_dict_urine中的每一个df，将每个df中的“+”，“UK","uk"，“uK","Uk","-"替换为np.nan
    for sheet in tab16_dict_urine.keys():
        tab16_dict_urine[sheet].replace(['+', 'UK', 'uk', 'uK', 'Uk', '-'], np.nan, inplace=True)

    st.markdown('## 尿白细胞（LEU）')
    # 根据”label“列的值不同进行分组计算tab16_dict_blood中每一个df中”尿白细胞（LEU）“列的非空值计数和空值计数，形成一个新的df，所有的df存入一个新的dict
    # 遍历tab16_dict_urine中的每一个df
    for sheet in tab16_dict_urine.keys():
        # 获取当前df
        df_1 = tab16_dict_urine[sheet]
        grouped_1 = df_1.groupby('label')['尿白细胞（LEU）']
        stats_df_1 = pd.DataFrame({
                '非空值计数': grouped_1.apply(lambda x: x.count()),
                '空值计数': grouped_1.apply(lambda x: x.isnull().sum())
                })
        # 为两组非空值计数的差异进行卡方检验
        if '试验组' in stats_df_1.index and '对照组' in stats_df_1.index:
            try:
                chi2_test_result = stats.chi2_contingency([stats_df_1.loc['试验组'], stats_df_1.loc['对照组']])
                # 在stats_df_1中添加新的列”检验方法“，”统计量“和”p值“
                stats_df_1['检验方法'] = '卡方检验'
                stats_df_1['统计量'] = chi2_test_result[0]
                stats_df_1['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        # 根据df_1中label列的值不同，分组统计df_1中”1.一般状况“列中不同值的计数和占比
        value_counts = grouped_1.value_counts().unstack().fillna(0)
        # 如果在df中能定位到两组，则进行卡方检验
        if '试验组' in value_counts.index and '对照组' in value_counts.index:
            try:
                chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
                # 为value_counts添加”检验方法“，”统计量“和”p值“三列
                value_counts['检验方法'] = '卡方检验'
                value_counts['统计量'] = chi2_test_result[0]
                value_counts['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        value_counts_percent = grouped_1.value_counts(normalize=True).unstack().fillna(0) * 100
        # 给value_counts_percent的列名加上“占比(%)”
        value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
        # 合并value_counts，value_counts_percent为stats_df_1_1
        stats_df_1_1 = pd.concat([value_counts, value_counts_percent], axis=1)
        st.write(sheet)
        st.write(stats_df_1)
        st.write(stats_df_1_1)


    st.markdown('## 尿红细胞（RBC）')
    # 根据”label“列的值不同进行分组计算tab16_dict_blood中每一个df中”尿红细胞（RBC）“列的非空值计数和空值计数，形成一个新的df，所有的df存入一个新的dict
    # 遍历tab16_dict_urine中的每一个df
    for sheet in tab16_dict_urine.keys():
        # 获取当前df
        df_2 = tab16_dict_urine[sheet]
        grouped_2 = df_2.groupby('label')['尿红细胞（RBC）']
        stats_df_2 = pd.DataFrame({
                '非空值计数': grouped_2.apply(lambda x: x.count()),
                '空值计数': grouped_2.apply(lambda x: x.isnull().sum())
                })
        # 为两组非空值计数的差异进行卡方检验
        if '试验组' in stats_df_2.index and '对照组' in stats_df_2.index:
            try:
                chi2_test_result = stats.chi2_contingency([stats_df_2.loc['试验组'], stats_df_2.loc['对照组']])
                # 在stats_df_2中添加新的列”检验方法“，”统计量“和”p值“
                stats_df_2['检验方法'] = '卡方检验'
                stats_df_2['统计量'] = chi2_test_result[0]
                stats_df_2['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        # 根据df_2中label列的值不同，分组统计df_2中”1.一般状况“列中不同值的计数和占比
        value_counts = grouped_2.value_counts().unstack().fillna(0)
        # 如果在df中能定位到两组，则进行卡方检验
        if '试验组' in value_counts.index and '对照组' in value_counts.index:
            try:
                chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
                # 为value_counts添加”检验方法“，”统计量“和”p值“三列
                value_counts['检验方法'] = '卡方检验'
                value_counts['统计量'] = chi2_test_result[0]
                value_counts['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        value_counts_percent = grouped_2.value_counts(normalize=True).unstack().fillna(0) * 100
        # 给value_counts_percent的列名加上“占比(%)”
        value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
        # 合并value_counts，value_counts_percent为stats_df_2_2
        stats_df_2_2 = pd.concat([value_counts, value_counts_percent], axis=1)
        st.write(sheet)
        st.write(stats_df_2)
        st.write(stats_df_2_2)
    
    st.markdown('## 尿蛋白（PRO）')
    # 根据”label“列的值不同进行分组计算tab16_dict_blood中每一个df中”尿蛋白（PRO）“列的非空值计数和空值计数，形成一个新的df，所有的df存入一个新的dict
    # 遍历tab16_dict_urine中的每一个df
    for sheet in tab16_dict_urine.keys():
        # 获取当前df
        df_3 = tab16_dict_urine[sheet]
        grouped_3 = df_3.groupby('label')['尿蛋白（PRO）']
        stats_df_3 = pd.DataFrame({
                '非空值计数': grouped_3.apply(lambda x: x.count()),
                '空值计数': grouped_3.apply(lambda x: x.isnull().sum())
                })
        # 为两组非空值计数的差异进行卡方检验
        if '试验组' in stats_df_3.index and '对照组' in stats_df_3.index:
            try:
                chi2_test_result = stats.chi2_contingency([stats_df_3.loc['试验组'], stats_df_3.loc['对照组']])
                # 在stats_df_3中添加新的列”检验方法“，”统计量“和”p值“
                stats_df_3['检验方法'] = '卡方检验'
                stats_df_3['统计量'] = chi2_test_result[0]
                stats_df_3['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        # 根据df_3中label列的值不同，分组统计df_3中”1.一般状况“列中不同值的计数和占比
        value_counts = grouped_3.value_counts().unstack().fillna(0)
        # 如果在df中能定位到两组，则进行卡方检验
        if '试验组' in value_counts.index and '对照组' in value_counts.index:
            try:
                chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
                # 为value_counts添加”检验方法“，”统计量“和”p值“三列
                value_counts['检验方法'] = '卡方检验'
                value_counts['统计量'] = chi2_test_result[0]
                value_counts['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        value_counts_percent = grouped_3.value_counts(normalize=True).unstack().fillna(0) * 100
        # 给value_counts_percent的列名加上“占比(%)”
        value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
        # 合并value_counts，value_counts_percent为stats_df_3_2
        stats_df_3_2 = pd.concat([value_counts, value_counts_percent], axis=1)
        st.write(sheet)
        st.write(stats_df_3)
        st.write(stats_df_3_2)
    st.markdown('## 尿酮体（KET）')
    # 根据”label“列的值不同进行分组计算tab16_dict_blood中每一个df中”尿酮体（KET）“列的非空值计数和空值计数，形成一个新的df，所有的df存入一个新的dict
    # 遍历tab16_dict_urine中的每一个df
    for sheet in tab16_dict_urine.keys():
        # 获取当前df
        df_4 = tab16_dict_urine[sheet]
        grouped_4 = df_4.groupby('label')['尿酮体（KET）']
        stats_df_4 = pd.DataFrame({
                '非空值计数': grouped_4.apply(lambda x: x.count()),
                '空值计数': grouped_4.apply(lambda x: x.isnull().sum())
                })
        # 为两组非空值计数的差异进行卡方检验
        if '试验组' in stats_df_4.index and '对照组' in stats_df_4.index:
            try:
                chi2_test_result = stats.chi2_contingency([stats_df_4.loc['试验组'], stats_df_4.loc['对照组']])
                # 在stats_df_4中添加新的列”检验方法“，”统计量“和”p值“
                stats_df_4['检验方法'] = '卡方检验'
                stats_df_4['统计量'] = chi2_test_result[0]
                stats_df_4['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        # 根据df_4中label列的值不同，分组统计df_4中”1.一般状况“列中不同值的计数和占比
        value_counts = grouped_4.value_counts().unstack().fillna(0)
        # 如果在df中能定位到两组，则进行卡方检验
        if '试验组' in value_counts.index and '对照组' in value_counts.index:
            try:
                chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
                # 为value_counts添加”检验方法“，”统计量“和”p值“三列
                value_counts['检验方法'] = '卡方检验'
                value_counts['统计量'] = chi2_test_result[0]
                value_counts['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        value_counts_percent = grouped_4.value_counts(normalize=True).unstack().fillna(0) * 100
        # 给value_counts_percent的列名加上“占比(%)”
        value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
        # 合并value_counts，value_counts_percent为stats_df_4_2
        stats_df_4_2 = pd.concat([value_counts, value_counts_percent], axis=1)
        st.write(sheet)
        st.write(stats_df_4)
        st.write(stats_df_4_2)
    st.markdown('## 尿糖（GLU）')
    # 根据”label“列的值不同进行分组计算tab16_dict_blood中每一个df中”尿糖（GLU）“列的非空值计数和空值计数，形成一个新的df，所有的df存入一个新的dict
    # 遍历tab16_dict_urine中的每一个df
    for sheet in tab16_dict_urine.keys():
        # 获取当前df
        df_5 = tab16_dict_urine[sheet]
        grouped_5 = df_5.groupby('label')['尿糖（GLU）']
        stats_df_5 = pd.DataFrame({
                '非空值计数': grouped_5.apply(lambda x: x.count()),
                '空值计数': grouped_5.apply(lambda x: x.isnull().sum())
                })
        # 为两组非空值计数的差异进行卡方检验
        if '试验组' in stats_df_5.index and '对照组' in stats_df_5.index:
            try:
                chi2_test_result = stats.chi2_contingency([stats_df_5.loc['试验组'], stats_df_5.loc['对照组']])
                # 在stats_df_5中添加新的列”检验方法“，”统计量“和”p值“
                stats_df_5['检验方法'] = '卡方检验'
                stats_df_5['统计量'] = chi2_test_result[0]
                stats_df_5['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        # 根据df_5中label列的值不同，分组统计df_5中”1.一般状况“列中不同值的计数和占比
        value_counts = grouped_5.value_counts().unstack().fillna(0)
        # 如果在df中能定位到两组，则进行卡方检验
        if '试验组' in value_counts.index and '对照组' in value_counts.index:
            try:
                chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
                # 为value_counts添加”检验方法“，”统计量“和”p值“三列
                value_counts['检验方法'] = '卡方检验'
                value_counts['统计量'] = chi2_test_result[0]
                value_counts['p值'] = chi2_test_result[1]
            except ValueError:
                pass
        value_counts_percent = grouped_5.value_counts(normalize=True).unstack().fillna(0) * 100
        # 给value_counts_percent的列名加上“占比(%)”
        value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
        # 合并value_counts，value_counts_percent为stats_df_5_2
        stats_df_5_2 = pd.concat([value_counts, value_counts_percent], axis=1)
        st.write(sheet)
        st.write(stats_df_5)
        st.write(stats_df_5_2)

        








