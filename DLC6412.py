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
# 在st.sidebar中添加一个按钮，用于上传xlsx的文件
st.error('目前的筛选文件中包括S01-003,这个病例只在前三个访视存在，所以目前涉及到V4的数据先不要填，填完V1-V3的之后，我把003患者加进去，再填V4的数据。')
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
    tab16_for1_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for1_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for1_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for1_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for1_dict_1['D1'] = tab16_for1_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for1_dict_1['D3'] = tab16_for1_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for1_dict_1['D5'] = tab16_for1_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for1_dict_1['D6'] = tab16_for1_dict_1.pop(key)
    tab16_for1_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for1_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for1_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for1_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for1_dict_2['D0'] = tab16_for1_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for1_dict_2['D2'] = tab16_for1_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for1_dict_2['D4'] = tab16_for1_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for1_dict_2['D7'] = tab16_for1_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for1_dict_2['研究完成'] = tab16_for1_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for1_dict_2['计划外'] = tab16_for1_dict_2.pop(key)
    # tab16_for1_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for1_dict_1.keys():
        columns_to_keep = [col for col in tab16_for1_dict_1[key].columns if '咽干口微渴' in col] + ['subject_id']
        tab16_for1_dict_1[key] = tab16_for1_dict_1[key][columns_to_keep]
    # tab16_for1_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for1_dict_2.keys():
        columns_to_keep = [col for col in tab16_for1_dict_2[key].columns if '咽干口微渴' in col] + ['subject_id']
        tab16_for1_dict_2[key] = tab16_for1_dict_2[key][columns_to_keep]
    # tab16_for1_dict_1中每个df设置subject_id列为索引
    for key in tab16_for1_dict_1.keys():
        tab16_for1_dict_1[key] = tab16_for1_dict_1[key].set_index('subject_id')
    # tab16_for1_dict_2中每个df设置subject_id列为索引
    for key in tab16_for1_dict_2.keys():
        tab16_for1_dict_2[key] = tab16_for1_dict_2[key].set_index('subject_id')
    # 将tab16_for1_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for1_df_1 = pd.concat(tab16_for1_dict_1, axis=1)
    # 将tab16_for1_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for1_df_2 = pd.concat(tab16_for1_dict_2, axis=1)
    # 重命名tab16_for1_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for1_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for1_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for1_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for1_df_1和tab16_for1_df_2按照索引横向合并
    tab16_for1_df = pd.concat([tab16_for1_df_1, tab16_for1_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for1_df = tab16_for1_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for1_df.columns:
        for idx in tab16_for1_df.index:
            value = tab16_for1_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for1_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for1_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for1_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for1_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for1_df['delta_D1'] = tab16_for1_df['患者自评D1'] - tab16_for1_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for1_df['delta_D2'] = tab16_for1_df['患者自评D2'] - tab16_for1_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for1_df['delta_D3'] = tab16_for1_df['患者自评D3'] - tab16_for1_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for1_df['delta_D4'] = tab16_for1_df['患者自评D4'] - tab16_for1_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for1_df['delta_D5'] = tab16_for1_df['患者自评D5'] - tab16_for1_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for1_df['delta_D6'] = tab16_for1_df['患者自评D6'] - tab16_for1_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for1_df['delta_D7'] = tab16_for1_df['患者自评D7'] - tab16_for1_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for1_df['delta_研究完成'] = tab16_for1_df['患者自评_研究完成'] - tab16_for1_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for1_df['delta_计划外'] = tab16_for1_df['患者自评_计划外'] - tab16_for1_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # delta_D1 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D1'] != '有效') & (tab16_for1_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    # 如果患者自评D0!=1,且delta_D2<0,则delta_D2值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D2'] < 0), 'delta_D2'] = '有效'
    # delta_D2 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D2'] != '有效') & (tab16_for1_df['delta_D2'].notna()), 'delta_D2'] = '无效'
    # 如果患者自评D0!=1,且delta_D3<0,则delta_D3值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D3'] < 0), 'delta_D3'] = '有效'
    # delta_D3 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D3'] != '有效') & (tab16_for1_df['delta_D3'].notna()), 'delta_D3'] = '无效'
    # 如果患者自评D0!=1,且delta_D4<0,则delta_D4值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D4'] < 0), 'delta_D4'] = '有效'
    # delta_D4 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D4'] != '有效') & (tab16_for1_df['delta_D4'].notna()), 'delta_D4'] = '无效'
    # 如果患者自评D0!=1,且delta_D5<0,则delta_D5值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D5'] < 0), 'delta_D5'] = '有效'
    # delta_D5 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D5'] != '有效') & (tab16_for1_df['delta_D5'].notna()), 'delta_D5'] = '无效'
    # 如果患者自评D0!=1,且delta_D6<0,则delta_D6值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D6'] < 0), 'delta_D6'] = '有效'
    # delta_D6 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D6'] != '有效') & (tab16_for1_df['delta_D6'].notna()), 'delta_D6'] = '无效'
    # 如果患者自评D0!=1,且delta_D7<0,则delta_D7值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D7'] < 0), 'delta_D7'] = '有效'
    # delta_D7 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D7'] != '有效') & (tab16_for1_df['delta_D7'].notna()), 'delta_D7'] = '无效'
    # 如果患者自评D0!=1,且delta_研究完成<0,则delta_研究完成值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_研究完成'] < 0), 'delta_研究完成'] = '有效'
    # delta_研究完成 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_研究完成'] != '有效') & (tab16_for1_df['delta_研究完成'].notna()), 'delta_研究完成'] = '无效'
    # 如果患者自评D0!=1,且delta_研究退出<0,则”delta_计划外“值更改为”有效“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_计划外'] < 0), 'delta_计划外'] = '有效'
    # delta_计划外 中除了”有效“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_计划外'] != '有效') & (tab16_for1_df['delta_计划外'].notna()), 'delta_计划外'] = '无效'
    


    
    
    
    
    
    
    
    
    
    
    
    
    st.write(tab16_for1_df)
   
    

  