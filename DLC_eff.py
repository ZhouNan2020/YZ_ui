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

    tab16_6_dict = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_6_dict[key] = tab16_dict[key]
    # 获取tab16_6_dict中每一个df包含字符串“1、咽部疼痛”的列，并将这些列和当前df的”subject_id“列一起，添加到一个新的dict（tab16_6_columns）中
    tab16_6_columns = {}
    for key in tab16_6_dict.keys():
        for column in tab16_6_dict[key].columns:
            if '1、咽部疼痛' in column:
                tab16_6_columns[key] = tab16_6_dict[key][['subject_id', column]]
    # 设置tab16_6_columns中的每一个df的索引列为”subject_id“
    for key in tab16_6_columns.keys():
        tab16_6_columns[key].set_index('subject_id', inplace=True)
    # 将tab16_6_columns中所有的df横向合并，索引列的值一一对应，得到一个新的df
    tab16_6 = pd.concat(tab16_6_columns.values(), axis=1)
    # 合并后将列名重命名为“咽部疼痛D1”，“咽部疼痛D2”，"咽部疼痛D3","咽部疼痛D4“
    tab16_6.columns = ["咽部疼痛V1", "咽部疼痛V2", "咽部疼痛V3", "咽部疼痛V4","咽部疼痛V5","咽部疼痛V6"]
    match = pd.read_excel('match.xlsx')
    # 遍历tab16_6的索引列，并将其中每一个值与match中的“index”进行比较
    # 如果match中的”index“列的值不存在与tab16_6索引列中，则将match中的”index“列的值添加到tab16_6中df的索引列中，对应行中其他列的值为nan
    for index in match['index']:
        if index not in tab16_6.index:
            tab16_6.loc[index] = [np.nan, np.nan, np.nan, np.nan]
    # 如果tab16_6的值中包括字符串“分”，则删掉这个字符串
    tab16_6 = tab16_6.replace('分', '', regex=True)
    # 将tab16_6中的值转换为float类型
    tab16_6 = tab16_6.astype(float)
    # 遍历tab16_6中的每一个值，使用iterrows()方法
    for column in tab16_6.columns:
        for idx in tab16_6.index:
            value = tab16_6.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_6.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_6.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_6.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif abs(value - 0.0) < 1e-6:  # 使用容差范围进行比较
                tab16_6.loc[idx, column] = 1
    # tab16_6中添加一列“label”
    tab16_6['label'] = np.nan
    # 如果tab16_6中的subject_id列的值出现在dlct的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"试验组"
    for index in dlct['index']:
        if index in tab16_6.index:
            tab16_6['label'][index] = '试验组'
    # 如果tab16_6中的subject_id列的值出现在dlcc的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"对照组"
    for index in dlcc['index']:
        if index in tab16_6.index:
            tab16_6['label'][index] = '对照组'
    # tab16_6增加一列”d2delta",值为"咽部疼痛D2"-"咽部疼痛D1"，如果"咽部疼痛D2"或"咽部疼痛D1"为空，则"d2delta"为空
    tab16_6['d2delta'] = tab16_6['咽部疼痛V2'] - tab16_6['咽部疼痛V1']
    # tab16_6增加一列”d3delta",值为"咽部疼痛D3"-"咽部疼痛D1"，如果"咽部疼痛D3"或"咽部疼痛D1"为空，则"d3delta"为空
    tab16_6['d3delta'] = tab16_6['咽部疼痛V3'] - tab16_6['咽部疼痛V1']
    # tab16_6增加一列”d4delta",值为"咽部疼痛D4"-"咽部疼痛D1"，如果"咽部疼痛D4"或"咽部疼痛D1"为空，则"d4delta"为空
    tab16_6['d4delta'] = tab16_6['咽部疼痛V4'] - tab16_6['咽部疼痛V1']
    # 给tab16_6添加一列“疗效”，默认为nan
    tab16_6['疗效'] = np.nan
    # 如果tab16_6中的“d2delta”列的值为<0，但是'咽部疼痛V4'列的值不为1，则在tab16_6中该行的“疗效”列中填入“改善”
    for idx in tab16_6.index:
        if tab16_6['d4delta'][idx] < 0 and tab16_6['咽部疼痛V4'][idx] != 1:
            tab16_6['疗效'][idx] = '改善'
    # 如果tab16_6中'咽部疼痛V4'列的值为1，则在tab16_6中该行的“疗效”列中填入“治愈”
    for idx in tab16_6.index:
        if tab16_6['咽部疼痛V4'][idx] == 1:
            tab16_6['疗效'][idx] = '治愈'
    # 如果tab16_6中的'咽部疼痛V4'列的值>'咽部疼痛V1'列的值或'd4delta'列的值＞0，则在tab16_6中该行的“疗效”列中填入“加重”
    for idx in tab16_6.index:
        if tab16_6['咽部疼痛V4'][idx] > tab16_6['咽部疼痛V1'][idx] or tab16_6['d4delta'][idx] > 0:
            tab16_6['疗效'][idx] = '加重'
    # 如果tab16_6中的'咽部疼痛V4'列的值=='咽部疼痛V1'列的值或'd4delta'列的值==0，则在tab16_6中该行的“疗效”列中填入“无效”
    for idx in tab16_6.index:
        if tab16_6['咽部疼痛V4'][idx] == tab16_6['咽部疼痛V1'][idx] or tab16_6['d4delta'][idx] == 0:
            tab16_6['疗效'][idx] = '无效'


    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值==”改善“的个数和nan值计数，存入一个df
    tab16_6_improve = tab16_6[tab16_6['疗效'] == '改善'].groupby('label')['疗效'].count()
    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值==”治愈“的个数和nan值计数，存入一个df
    tab16_6_cure = tab16_6[tab16_6['疗效'] == '治愈'].groupby('label')['疗效'].count()
    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值==”加重“的个数和nan值计数，存入一个df
    tab16_6_worse = tab16_6[tab16_6['疗效'] == '加重'].groupby('label')['疗效'].count()
    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值==”无效“的个数和nan值计数，存入一个df
    tab16_6_invalid = tab16_6[tab16_6['疗效'] == '无效'].groupby('label')['疗效'].count()
    # 横向拼接tab16_6_improve，tab16_6_cure，tab16_6_worse，tab16_6_invalid，存入一个df
    tab16_6_improve_cure = pd.concat([tab16_6_improve, tab16_6_cure, tab16_6_worse, tab16_6_invalid], axis=1)
    # 重命名tab16_6_improve_cure的列名
    tab16_6_improve_cure.columns = ['改善', '治愈', '加重', '无效']
    # tab16_6_improve_cure中的nan值填充为0
    tab16_6_improve_cure = tab16_6_improve_cure.fillna(0)
    
    # 删除tab16_6_improve_cure中所有值为0的列
    tab16_6_improve_cure = tab16_6_improve_cure.loc[:, (tab16_6_improve_cure != 0).any(axis=0)]
    # 针对tab16_6_improve_cure两行,对列变量的差异进行卡方检验，记录卡方值和p值
    chi2, p = stats.chi2_contingency(tab16_6_improve_cure)[0:2]
    # 添加一列统计量，再添加一列p值
    tab16_6_improve_cure['统计量'] = np.nan
    tab16_6_improve_cure['p值'] = np.nan
    tab16_6_improve_cure['统计量']['试验组'] = chi2
    tab16_6_improve_cure['p值']['试验组'] = p
    st.write(tab16_6_improve_cure)
    
    # 为tab16_6增加一列“治愈天数”，默认为nan
    tab16_6['治愈天数'] = np.nan

    # 寻找tab16_6中“'咽部疼痛V1'”列不为1的行，然后按现有的列的顺序遍历该行中"咽部疼痛V1", "咽部疼痛V2", "咽部疼痛V3", "咽部疼痛V4"列的值，寻找该行值首次出现1的列，然后将该列的列名赋值给“治愈天数”列
    for idx in tab16_6.index:
        if tab16_6.loc[idx, '咽部疼痛V1'] != 1:
            for column in ['咽部疼痛V1', '咽部疼痛V2', '咽部疼痛V3', '咽部疼痛V4']:
                if tab16_6.loc[idx, column] == 1:
                    tab16_6.loc[idx, '治愈天数'] = column
                    break
    # 为tab16_6增加一列“改善天数”，默认为nan
    tab16_6['改善天数'] = np.nan
    # 寻找tab16_6中“'咽部疼痛V1'”列不为1的行，然后按现有的列的顺序遍历该行中"d2delta", "d3delta", "d4delta"列的值，寻找该行值在这几列中首次出现小于0的值所在的列，然后将该列的列名赋值给“改善天数”列   
    
    for idx in tab16_6.index:
        if tab16_6.loc[idx, '咽部疼痛V1'] != 1:
            for column in ['d2delta', 'd3delta', 'd4delta']:
                if tab16_6.loc[idx, column] < 0:
                    tab16_6.loc[idx, '改善天数'] = column
                    break
    # 替换tab16_6中“治愈天数”列中的值，如果是“咽部疼痛V1”则替换为int（1），如果是“咽部疼痛V2”则替换为int(2)，如果是“咽部疼痛V3”则替换为int(4)，如果是“咽部疼痛V4”则替换为int(7)
    tab16_6['治愈天数'] = tab16_6['治愈天数'].replace({'咽部疼痛V1': 1, '咽部疼痛V2': 2, '咽部疼痛V3': 4, '咽部疼痛V4': 7})
    # 替换tab16_6中“改善天数”列中的值，如果是“d2delta”则替换为int（2），如果是“d3delta”则替换为int(4)，如果是“d4delta”则替换为int(7)
    tab16_6['改善天数'] = tab16_6['改善天数'].replace({'d2delta': 2, 'd3delta': 4, 'd4delta': 7})
    # 把tab16_6中“治愈天数”和“改善天数”列中的值转换为float型
    tab16_6['治愈天数'] = tab16_6['治愈天数'].astype(float)
    tab16_6['改善天数'] = tab16_6['改善天数'].astype(float)
     
   


    tab16km1 = tab16_6.copy()
    # 删除tab16km1中”咽部疼痛V5“和”咽部疼痛V6“列
    tab16km1 = tab16km1.drop(['咽部疼痛V5', '咽部疼痛V6'], axis=1)
    # 将tab16km1中”疗效“列中的”治愈“和”改善“替换为1，其余非空值替换为0，空值不变
    tab16km1['疗效'] = tab16km1['疗效'].replace({'治愈': 1, '改善': 1})
    # label列中的“试验组”替换为1，对照组替换为0
    tab16km1['label'] = tab16km1['label'].replace({'试验组': 1})
    tab16km1['label'] = tab16km1['label'].replace({'对照组': 0})
    #  如果tab16km1中的行在任意位置有空值，就将该行删除
    #tab16km1 = tab16km1.dropna(axis=0, how='any')
    # 
    # 使用当前列的众数填充tab16km1中的所有列的缺失值
    for column in tab16km1.columns:
        tab16km1[column].fillna(tab16km1[column].mode()[0], inplace=True)

    

    # 针对tab16km1做km生存分析，以“改善天数”为时间，以“疗效”为事件，label为分组变量
    kmf = KaplanMeierFitter()
    tab16km1['改善天数'] = tab16km1['改善天数'].astype(float)
    tab16km1['疗效'] = tab16km1['疗效'].astype(float)
    kmf.fit(tab16km1['改善天数'], tab16km1['疗效'])
    fig, ax = plt.subplots()
    results = []
    for label in tab16km1['label'].unique():
        kmf.fit(tab16km1.loc[tab16km1['label'] == label, '改善天数'], 
                tab16km1.loc[tab16km1['label'] == label, '疗效'])
        # 更改图例，1为试验组，0为对照组
        if label == 1:
            kmf.plot(ax=ax, label='试验组')
        else:
            kmf.plot(ax=ax, label='对照组')
        results.append(kmf.survival_function_)
    ax.legend(prop=font)
    # 设置x轴标签
    ax.set_xlabel('改善天数',fontproperties=font)
    # 设置y轴标签
    ax.set_ylabel('改善率',fontproperties=font)
    st.pyplot(fig)
    # 使用log_rank检验两组差异
    result = logrank_test(results[0], results[1])
    # 结果形成一个df
    df = pd.DataFrame({
        't-statistic': [result.test_statistic],
        'p-value': [result.p_value]
    })
    # 以st.write形式呈现
    st.write(df)
    # 横向拼接kmf.survival_function_、kmf.cumulative_density_ 和 kmf.confidence_interval_
    dfkm1 = pd.concat([kmf.survival_function_, kmf.cumulative_density_, kmf.confidence_interval_], axis=1)
    # 重命名列名
    dfkm1.columns = ['生存函数', '累积密度函数', '95%CI下限', '95%CI上限']
    # 以st.write形式呈现
    st.write(dfkm1)
 
    
    tab16km2 = tab16_6.copy()
    # 删除tab16km1中”咽部疼痛V5“和”咽部疼痛V6“列
    tab16km2 = tab16km2.drop(['咽部疼痛V5', '咽部疼痛V6'], axis=1)
    # 将tab16km1中”疗效“列中的”治愈“替换为1，”改善“替换为0，其余非空值替换为0，空值不变
    tab16km2['疗效'] = tab16km2['疗效'].replace({'治愈': 1})
    tab16km2['疗效'] = tab16km2['疗效'].replace({'改善': 0})
    # label列中的“试验组”替换为1，对照组替换为0
    tab16km2['label'] = tab16km2['label'].replace({'试验组': 1})
    tab16km2['label'] = tab16km2['label'].replace({'对照组': 0})
    # 如果tab16km2中的行在任意位置有空值，就将该行删除
    # tab16km2 = tab16km2.dropna(axis=0, how='any')
    # 
    # 使用当前列的众数填充tab16km2中的所有列的缺失值
    for column in tab16km2.columns:
        tab16km2[column].fillna(tab16km2[column].mode()[0], inplace=True)

    # 针对tab16km2做km生存分析，以“治愈天数”为时间，以“疗效”为事件，label为分组变量
    kmf = KaplanMeierFitter()
    tab16km2['治愈天数'] = tab16km2['治愈天数'].astype(float)
    tab16km2['疗效'] = tab16km2['疗效'].astype(float)
    kmf.fit(tab16km2['治愈天数'], tab16km2['疗效'])
    fig, ax = plt.subplots()
    results = []
    for label in tab16km2['label'].unique():
        kmf.fit(tab16km2.loc[tab16km2['label'] == label, '治愈天数'], 
                tab16km2.loc[tab16km2['label'] == label, '疗效'])
        # 更改图例，1为试验组，0为对照组
        if label == 1:
            kmf.plot(ax=ax, label='试验组')
        else:
            kmf.plot(ax=ax, label='对照组')
        results.append(kmf.survival_function_)
    ax.legend(prop=font)
    # 设置x轴标签
    ax.set_xlabel('治愈天数',fontproperties=font)
    # 设置y轴标签
    ax.set_ylabel('治愈率',fontproperties=font)
    st.pyplot(fig)
    # 使用log_rank检验两组差异
    result = logrank_test(results[0], results[1])
    # 结果形成一个df
    df = pd.DataFrame({
        't-statistic': [result.test_statistic],
        'p-value': [result.p_value]
    })
    # 以st.write形式呈现
    st.write(df)
    # 横向拼接kmf.survival_function_、kmf.cumulative_density_ 和 kmf.confidence_interval_，形成一个新的df
    dfkm2=pd.concat([kmf.survival_function_, kmf.cumulative_density_, kmf.confidence_interval_], axis=1)
    # 重命名列名
    dfkm2.columns = ['生存函数', '累积密度函数', '95%CI下限', '95%CI上限']
    # 以st.write形式呈现
    st.write(dfkm2)

    st.write(tab16_6)
    # 
    
    



    




    
    
    





