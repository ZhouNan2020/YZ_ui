
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from scipy import stats

#%%
font = font_manager.FontProperties(fname='simhei.ttf')

parameters = {'xtick.labelsize': 20,
              'ytick.labelsize': 20,
              
              'axes.unicode_minus':False}
plt.rcParams.update(parameters)
#%%
st.error('目前的筛选文件中包括S01-003,这个病例只在前三个访视存在，所以目前涉及到V4的数据先不要填，填完V1-V3的之后，我把003患者加进去，再填V4的数据。')
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







# 从tab16_dict中提取出所有key名包含”#血常规“的df，形成一个新的dict
    tab16_dict_bloche = {}
    for sheet in tab16_dict.keys():
        # 提取所有包含”#血常规“但是不包括”#血常规其他异常结果“的key
        if '#血生化' in sheet and '#血生化其他异常结果' not in sheet:
            tab16_dict_bloche[sheet] = tab16_dict[sheet]

    


    # 根据”label“列的值不同进行分组计算tab16_dict_bloche中每一个df中”超敏C反应蛋白（hs-CRP）“列的非空值计数、空值计数、平均值、标准差，中位数，Q1，Q3，最小值，最大值，形成一个新的df，存入新的dict中
    # 创建一个新的字典来存储结果
    result_dict_8 = {}
    # 遍历tab16_dict_bloche中的每一个df
    for sheet in tab16_dict_bloche.keys():
        # 获取当前df
        df = tab16_dict_bloche[sheet]
        
        # 每一个df设置subject_id为索引
        df.set_index('subject_id', inplace=True)
        # 取每个df的"超敏C反应蛋白（hs-CRP）"列,存为一个新的df
        ndf = df[['超敏C反应蛋白（hs-CRP）']]
        # 如果ndf中有值为字符串”<10“，则将其替换为9.9
        ndf['超敏C反应蛋白（hs-CRP）'] = ndf['超敏C反应蛋白（hs-CRP）'].replace('<10', 9.9)
        
        # 如果ndf中有值为字符串”>3“，则将其替换为3.1
        ndf['超敏C反应蛋白（hs-CRP）'] = ndf['超敏C反应蛋白（hs-CRP）'].replace('>3', 3.1)
        # 如果ndf中有值为字符串”UK“，则将其替换为np.nan 
        ndf['超敏C反应蛋白（hs-CRP）'] = ndf['超敏C反应蛋白（hs-CRP）'].replace('UK', np.nan)
        # 尝试将ndf转为numreic，如果遇到异常值不能转换则跳过
        ndf['超敏C反应蛋白（hs-CRP）'] = pd.to_numeric(ndf['超敏C反应蛋白（hs-CRP）'], errors='coerce')

        
        # 判断：如果索引值中包括字符串”S01“，则”超敏C反应蛋白（hs-CRP）“列中值<4的值替换为正常，其余替换为异常，空值依然为np.nan
        if 'S01' in ndf.index:
            ndf.loc[ndf['超敏C反应蛋白（hs-CRP）'] < 4, '超敏C反应蛋白（hs-CRP）'] = '正常'
            ndf.loc[(ndf['超敏C反应蛋白（hs-CRP）'] != '正常') & (ndf['超敏C反应蛋白（hs-CRP）'].notna()), '超敏C反应蛋白（hs-CRP）'] = '异常'
        
        # 判断：如果索引值中包括字符串”S03“，则”超敏C反应蛋白（hs-CRP）“列中值<10的值替换为正常，其余替换为异常，空值依然为np.nan
        if 'S03' in ndf.index:
            ndf.loc[(ndf['超敏C反应蛋白（hs-CRP）'] < 10) | (ndf['超敏C反应蛋白（hs-CRP）'] == '<10'), '超敏C反应蛋白（hs-CRP）'] = '正常'
            ndf.loc[(ndf['超敏C反应蛋白（hs-CRP）'] != '正常') & (ndf['超敏C反应蛋白（hs-CRP）'].notna()), '超敏C反应蛋白（hs-CRP）'] = '异常'
        # 判断：如果索引值中包括字符串”S04“，则”超敏C反应蛋白（hs-CRP）“列中值<3的值替换为正常，其余替换为异常，空值依然为np.nan
        if 'S04' in ndf.index:
            ndf.loc[ndf['超敏C反应蛋白（hs-CRP）'] < 3, '超敏C反应蛋白（hs-CRP）'] = '正常'
            ndf.loc[(ndf['超敏C反应蛋白（hs-CRP）'] != '正常') & (ndf['超敏C反应蛋白（hs-CRP）'].notna()), '超敏C反应蛋白（hs-CRP）'] = '异常'
        st.write(ndf)
        
