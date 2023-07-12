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


    st.markdown('## 1.咽干')
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
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for1_df.loc[(tab16_for1_df['delta_D1'] != '有效') & (tab16_for1_df['delta_D1'] != '治愈') & (tab16_for1_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for1_df.loc[(tab16_for1_df['delta_D'+str(i)] != '有效') & (tab16_for1_df['delta_D'+str(i)] != '治愈') & (tab16_for1_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for1_df.loc[(tab16_for1_df['患者自评D0'] != 1) & (tab16_for1_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for1_df.loc[(tab16_for1_df['delta_'+column] != '有效') & (tab16_for1_df['delta_'+column] != '治愈') & (tab16_for1_df['delta_'+column].notna()), 'delta_'+column] = '无效'
    # tab16_for1_df增加一列”label“，值默认为nan
    tab16_for1_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for1_df的索引中，则tab16_for1_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for1_df.index:
            tab16_for1_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for1_df的索引中，则tab16_for1_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for1_df.index:
            tab16_for1_df.loc[i, 'label'] = '对照组'
    code = pd.read_excel('code.xlsx')
    # code中空值使用”未知“填充
    code = code.fillna('未知')
    # code只保留PT列中包含字符串”咽炎“，”咽喉炎“和”扁桃体炎“的行
    code = code[code['PT'].str.contains('咽炎|咽喉炎|扁桃体炎')]
    # code增加一个列，count，值为1
    code['count'] = 1
    # pivot_table，index为code中的“subject_id”，columns为tab16_for1_df中的“PT”列，values为code中的“count”，aggfunc为sum
    code_pivot = pd.pivot_table(code, index='subject_id', columns='PT', values='count', aggfunc='sum')
    # 将code_pivot中的nan值填充为0
    code_pivot = code_pivot.fillna(0)
    # 将code_pivot中的值转换为int型
    code_pivot = code_pivot.astype(int)
    # code_pivot与tab16_for1_df按照索引横向合并，
    tab16_for1_df = pd.concat([tab16_for1_df, code_pivot], axis=1)
    # 提取出tab16_for1_df中咽喉炎列不为0的行，按照label值的不同，计算delta_D2到delta_D7列不同值的计数，存入一个新的dataframe中
    # 提取出tab16_for1_df中咽喉炎列不为0的行
    tab16_for1_df_filtered_1 = tab16_for1_df[tab16_for1_df['咽喉炎'] != 0]
    # 初始化一个空的dataframe用于存储每个循环的结果
    # 按照label值的不同，计算delta_D2到delta_D7列不同值的计数，存入new_df_1中
    for i in range(2, 8):
        new_df_1 = tab16_for1_df_filtered_1.groupby('label')['delta_D'+str(i)].value_counts().unstack(fill_value=0)
    
    # 提取出tab16_for1_df中咽炎列不为0的行
    tab16_for1_df_filtered_2 = tab16_for1_df[tab16_for1_df['咽炎'] != 0]
    # 按照label值的不同，计算delta_D2到delta_D7列不同值的计数，存入new_df_2中
    for i in range(2, 8):
        new_df_2 = tab16_for1_df_filtered_2.groupby('label')['delta_D'+str(i)].value_counts().unstack(fill_value=0)
    
    # 提取出tab16_for1_df中扁桃体炎列不为0的行
    tab16_for1_df_filtered_3 = tab16_for1_df[tab16_for1_df['扁桃体炎'] != 0]
    # 按照label值的不同，计算delta_D2到delta_D7列不同值的计数，存入new_df_3中
    for i in range(2, 8):
        new_df_3 = tab16_for1_df_filtered_3.groupby('label')['delta_D'+str(i)].value_counts().unstack(fill_value=0)
    
    # 使用st.write()展示以上df
    st.write(new_df_1)
    st.write(new_df_2)
    st.write(new_df_3)

    st.write(tab16_for1_df)