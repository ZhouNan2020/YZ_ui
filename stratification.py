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

    # 获取tab16_dict中的“访视1筛选-基线（0天）#96616#咽部充血”和“访视4研究第7天 #96668#咽部充血”两个df
    df1 = tab16_dict['访视1筛选-基线（0天）#96616#咽部充血']
    df4 = tab16_dict['访视4研究第7天 #96668#咽部充血']
    # 设置两个表的索引为subject_id
    df1.set_index('subject_id', inplace=True)
    df4.set_index('subject_id', inplace=True)
    # 将两个表的检查日期列的数据类型转换为datetime，如果转换失败，则将该行的数据删除
    df1['检查日期'] = pd.to_datetime(df1['检查日期'], errors='coerce')
    df4['检查日期'] = pd.to_datetime(df4['检查日期'], errors='coerce')
    # 遍历df的“检查结果评分”列中每一个值
    for i in df1['检查结果评分'].values:
        # 如果该值为nan，则跳过
        if pd.isna(i):
            continue
        # 如果7<=值<=10，则替换为4
        elif 7 <= i <= 10:
            df1['检查结果评分'].replace(i, 4, inplace=True)
        # 如果4<=值<=6，则替换为3
        elif 4 <= i <= 6:
            df1['检查结果评分'].replace(i, 3, inplace=True)
        # 如果1<=值<=3，则替换为2
        elif 1 <= i <= 3:
            df1['检查结果评分'].replace(i, 2, inplace=True)
        # 如果值==0，则替换为1
        elif i == 0:
            df1['检查结果评分'].replace(i, 1, inplace=True)
    # 遍历df4的“检查结果评分”列中每一个值
    for i in df4['检查结果评分'].values:
        # 如果该值为nan，则跳过
        if pd.isna(i):
            continue
        # 如果7<=值<=10，则替换为4
        elif 7 <= i <= 10:
            df4['检查结果评分'].replace(i, 4, inplace=True)
        # 如果4<=值<=6，则替换为3
        elif 4 <= i <= 6:
            df4['检查结果评分'].replace(i, 3, inplace=True)
        # 如果1<=值<=3，则替换为2
        elif 1 <= i <= 3:
            df4['检查结果评分'].replace(i, 2, inplace=True)
        # 如果值==0，则替换为1
        elif i == 0:
            df4['检查结果评分'].replace(i, 1, inplace=True)
    # df4增加一个疗效列
    df4['疗效'] = np.nan
    # 按照索引的对应关系，如果df1中的检查结果评分不为1，并且df4中的检查结果评分为1，或者df1中检查结果评分不为1，df4中的检查结果评分不为1，且df4的检查结果评分小于df1的检查结果评分，则在df4中的疗效列中填入“有效”
    for index in df4.index:
        if df1.loc[index, '检查结果评分'] != 1 and df4.loc[index, '检查结果评分'] == 1:
            df4.loc[index, '疗效'] = '有效'
        elif df1.loc[index, '检查结果评分'] != 1 and df4.loc[index, '检查结果评分'] != 1 and df4.loc[index, '检查结果评分'] < df1.loc[index, '检查结果评分']:
            df4.loc[index, '疗效'] = '有效'
    
    # 按照索引的对应关系，如果df1中检查结果评分不为1，df4中的检查结果评分不为1，且df4的检查结果评分大于或等于df1的检查结果评分，则在df4中的疗效列中填入“有效”
    for index in df4.index:
        if df1.loc[index, '检查结果评分'] != 1 and df4.loc[index, '检查结果评分'] != 1 and df4.loc[index, '检查结果评分'] >= df1.loc[index, '检查结果评分']:
            df4.loc[index, '疗效'] = '有效'
    
    # 使用df4的检查日期-df1的检查日期，按照索引的对应关系，计算出每个受试者的检查时间差，以天为单位
    df4['时间差'] = df4['检查日期'] - df1['检查日期']
    df4['时间差'] = df4['时间差'].apply(lambda x: x.days)
    # 将df4中的时间差列的数据类型转换为int
    df4['时间差'] = df4['时间差'].astype(float)
    # 选择df4中label为“对照组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    df4_1 = df4[df4['label'] == '试验组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    df4_1['百分比'] = df4_1.sum(axis=1) / df4_1.sum(axis=1).sum()

    # 选择df4中label为“治疗组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    df4_2 = df4[df4['label'] == '对照组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    df4_2['百分比'] = df4_2.sum(axis=1) / df4_2.sum(axis=1).sum()
    # 把索引列的名字改为“病程“
    df4_1.index.name = '病程'
    df4_2.index.name = '病程'
    st.write('## 咽部充血')
    st.write('试验组')
    st.write(df4_1)
    st.write('对照组')
    st.write(df4_2)



    #%%

    # 获取tab16_dict中的“访视1筛选-基线（0天）#96616#咽部充血”和“访视4研究第7天 #96668#咽部充血”两个df
    follicle1 = tab16_dict['访视1筛选-基线（0天）#96617#咽部滤泡']
    follicle4 = tab16_dict['访视4研究第7天 #96669#咽部滤泡']
    # 设置两个表的索引为subject_id
    follicle1.set_index('subject_id', inplace=True)
    follicle4.set_index('subject_id', inplace=True)
    # 将两个表的检查日期列的数据类型转换为datetime，如果转换失败，则将该行的数据删除
    follicle1['检查日期'] = pd.to_datetime(follicle1['检查日期'], errors='coerce')
    follicle4['检查日期'] = pd.to_datetime(follicle4['检查日期'], errors='coerce')
    # 只保留follicle1中”检查结果“列的值为“有滤泡”的行
    follicle1 = follicle1[follicle1['检查结果'] == '有滤泡']
    # follicle4保留和follicle1索引相同的行
    follicle4 = follicle4.loc[follicle1.index]
    # follicle4增加一个疗效列
    follicle4['疗效'] = np.nan
    # 如果follicle4中”检查结果“列的值中有nan或NA，则疗效列填入"未查“
    follicle4.loc[follicle4['检查结果'].isna(), '疗效'] = '未查'
    # 如果follicle4中”检查结果“列的值包含字符串”有效“或”痊愈“，则疗效列中填入”有效“
    follicle4.loc[follicle4['检查结果'].str.contains('有效|痊愈', na=False), '疗效'] = '有效'
    
    
    # 使用follicle4的检查日期-follicle1的检查日期，按照索引的对应关系，计算出每个受试者的检查时间差，以天为单位
    follicle4['时间差'] = follicle4['检查日期'] - follicle1['检查日期']
    follicle4['时间差'] = follicle4['时间差'].apply(lambda x: x.days)
    # 将follicle4中的时间差列的数据类型转换为int
    follicle4['时间差'] = follicle4['时间差'].astype(float)
    # 选择follicle4中label为“对照组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    follicle4_1 = follicle4[follicle4['label'] == '试验组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    follicle4_1['百分比'] = follicle4_1.sum(axis=1) / follicle4_1.sum(axis=1).sum()

    # 选择follicle4中label为“治疗组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    follicle4_2 = follicle4[follicle4['label'] == '对照组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    follicle4_2['百分比'] = follicle4_2.sum(axis=1) / follicle4_2.sum(axis=1).sum()
    # 把索引列的名字改为“病程“
    follicle4_1.index.name = '病程'
    follicle4_2.index.name = '病程'
    st.write('## 咽部滤泡')
    st.write('试验组')
    st.write(follicle4_1)
    st.write('对照组')
    st.write(follicle4_2)
    

    #%%
    # 获取tab16_dict中的“访视1筛选-基线（0天）#96616#咽部充血”和“访视4研究第7天 #96668#咽部充血”两个df
    tonsil1 = tab16_dict['访视1筛选-基线（0天）#96618#扁桃体肿大']
    tonsil4 = tab16_dict['访视4研究第7天 #96670#扁桃体肿大']
    # 设置两个表的索引为subject_id
    tonsil1.set_index('subject_id', inplace=True)
    tonsil4.set_index('subject_id', inplace=True)
    # 将两个表的检查日期列的数据类型转换为datetime，如果转换失败，则将该行的数据删除
    tonsil1['检查日期'] = pd.to_datetime(tonsil1['检查日期'], errors='coerce')
    tonsil4['检查日期'] = pd.to_datetime(tonsil4['检查日期'], errors='coerce')
    # 如果tonsil1中”检查结果“列的值为“无肿大”，则删除该行
    tonsil1 = tonsil1[tonsil1['检查结果'] != '无肿大']
    # tonsil4保留和tonsil1索引相同的行
    tonsil4 = tonsil4.loc[tonsil1.index]
    # tonsil4增加一个疗效列
    tonsil4['疗效'] = np.nan
    # 如果tonsil4中”检查结果“列的值中有nan或NA，则疗效列填入"未查“
    tonsil1['检查结果'] = tonsil1['检查结果'].fillna(np.nan).astype(str)
    tonsil4['检查结果'] = tonsil4['检查结果'].fillna(np.nan).astype(str)
    # 如果tonsil1中”检查结果“列的值包含字符串Ⅰ，则替换为1，如果包含字符串Ⅱ，则替换为2，如果包含字符串Ⅲ，则替换为3，如果包含字符串Ⅳ，则替换为4
    tonsil1['检查结果'] = tonsil1['检查结果'].astype(str)
    tonsil1.loc[tonsil1['检查结果'].str.contains('Ⅰ', na=False), '检查结果'] = 1
    tonsil1.loc[tonsil1['检查结果'].str.contains('Ⅱ', na=False), '检查结果'] = 2
    tonsil1.loc[tonsil1['检查结果'].str.contains('Ⅲ', na=False), '检查结果'] = 3
    
    # 如果tonsil4中”检查结果“列的值包含字符串Ⅰ，则替换为1，如果包含字符串Ⅱ，则替换为2，如果包含字符串Ⅲ，则替换为3，如果包含字符串Ⅳ，则替换为4
    # 如果”无肿大“则替换为0
    tonsil4['检查结果'] = tonsil4['检查结果'].astype(str)
    tonsil4.loc[tonsil4['检查结果'].str.contains('Ⅰ', na=False), '检查结果'] = 1
    tonsil4.loc[tonsil4['检查结果'].str.contains('Ⅱ', na=False), '检查结果'] = 2
    tonsil4.loc[tonsil4['检查结果'].str.contains('Ⅲ', na=False), '检查结果'] = 3
    tonsil4.loc[tonsil4['检查结果'].str.contains('无肿大', na=False), '检查结果'] = 0
    # 空值均填充为nan
    tonsil1['检查结果'] = tonsil1['检查结果'].fillna(np.nan)
    tonsil4['检查结果'] = tonsil4['检查结果'].fillna(np.nan)
    # 将两个df的检查结果列转换为float类型
    tonsil1['检查结果'] = tonsil1['检查结果'].astype(float)
    tonsil4['检查结果'] = tonsil4['检查结果'].astype(float)
    # 使用tonsil4的检查结果-tonsil1的检查结果，按照索引的对应关系，计算出每个受试者的疗效，以天为单位，得到的结果按索引合并到tonsil4中
    tonsil4['评分差'] = tonsil4['检查结果'] - tonsil1['检查结果']
    # 如果评分差列值＜0，则疗效列填入“无效”
    tonsil4.loc[tonsil4['评分差'] < 0, '疗效'] = '无效'
    # 如果评分差列值=0或＞0，则疗效列填入“有效”
    tonsil4.loc[tonsil4['评分差'] >= 0, '疗效'] = '有效'

    
    
    # 使用tonsil4的检查日期-tonsil1的检查日期，按照索引的对应关系，计算出每个受试者的检查时间差，以天为单位
    tonsil4['时间差'] = tonsil4['检查日期'] - tonsil1['检查日期']
    tonsil4['时间差'] = tonsil4['时间差'].apply(lambda x: x.days)
    # 将tonsil4中的时间差列的数据类型转换为int
    tonsil4['时间差'] = tonsil4['时间差'].astype(float)
    # 选择tonsil4中label为“对照组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    tonsil4_1 = tonsil4[tonsil4['label'] == '试验组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    tonsil4_1['百分比'] = tonsil4_1.sum(axis=1) / tonsil4_1.sum(axis=1).sum()

    # 选择tonsil4中label为“治疗组”的数据，以时间差列为索引，疗效列为列，计算出每个时间差下的疗效的数量
    tonsil4_2 = tonsil4[tonsil4['label'] == '对照组'].pivot_table(index='时间差', columns='疗效', aggfunc='size')
    # 计算百分比并添加为新列
    tonsil4_2['百分比'] = tonsil4_2.sum(axis=1) / tonsil4_2.sum(axis=1).sum()
    # 把索引列的名字改为“病程“
    tonsil4_1.index.name = '病程'
    tonsil4_2.index.name = '病程'
    st.write('## 扁桃体肿大')
    st.write('试验组')
    st.write(tonsil4_1)
    st.write('对照组')
    st.write(tonsil4_2)