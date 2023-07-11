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


    tab16_for1_dict = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#咽部充血' in key:
            tab16_for1_dict[key] = tab16_dict[key]

    # 获取tab16_6_dict中每一个df包含字符串“检查结果评分”的列，并将这些列和当前df的”subject_id“列一起，添加到一个新的dict（tab16_for1_columns）中
    tab16_for1_columns = {}
    for key in tab16_for1_dict.keys():
        for column in tab16_for1_dict[key].columns:
            if '检查结果评分' in column:
                tab16_for1_columns[key] = tab16_for1_dict[key][['subject_id', column]]

    # 设置tab16_for1_columns中的每一个df的索引列为”subject_id“
    for key in tab16_for1_columns.keys():
        tab16_for1_columns[key].set_index('subject_id', inplace=True)
    # 将tab16_6_columns中所有的df横向合并，索引列的值一一对应，得到一个新的df（tab16_for1）
    tab16_for1 = pd.concat(tab16_for1_columns.values(), axis=1)
    # 合并后将列名重命名为“咽部充血V1”，“咽部充血V2”，"咽部充血V3","咽部充血V4“,"咽部充血V5"，“咽部充血V6"
    tab16_for1.columns = ['咽部充血V1', '咽部充血V2', '咽部充血V3', '咽部充血V4', '咽部充血V5', '咽部充血V6']
    match = pd.read_excel('match.xlsx')
    # 遍历tab16_6的索引列，并将其中每一个值与match中的“index”进行比较
    # 如果match中的”index“列的值不存在与tab16_6索引列中，则将match中的”index“列的值添加到tab16_6中df的索引列中，对应行中其他列的值为nan
    for index in match['index']:
        if index not in tab16_for1.index:
            tab16_for1.loc[index] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    # 将tab16_6中的索引列重命名为“subject_id”
    tab16_for1 = tab16_for1.replace('分', '', regex=True)
    # 使用pd.to_numeric将tab16_6中的值转换为float类型,并将转换失败的值替换为nan
    tab16_for1 = tab16_for1.apply(pd.to_numeric, errors='coerce')
    # 将tab16_6中的值转换为float类型
    tab16_for1 = tab16_for1.astype(float)
    for column in tab16_for1.columns:
        for idx in tab16_for1.index:
            value = tab16_for1.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for1.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for1.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for1.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for1.loc[idx, column] = 1
    
    # tab16_6中添加一列“label”
    tab16_for1['label'] = np.nan
    # 如果tab16_6中的subject_id列的值出现在dlct的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"试验组"
    for index in dlct['index']:
        if index in tab16_for1.index:
            tab16_for1['label'][index] = '试验组'
    # 如果tab16_6中的subject_id列的值出现在dlcc的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"对照组"
    for index in dlcc['index']:
        if index in tab16_for1.index:
            tab16_for1['label'][index] = '对照组'
    # tab16_for1增加一列”d2delta",值为"咽部充血V2"-"咽部充血V1"，如果"咽部充血V2"或"咽部充血V1"为空，则"d2delta"为空
    tab16_for1['d2delta'] = tab16_for1['咽部充血V2'] - tab16_for1['咽部充血V1']
    # tab16_for1增加一列”d3delta",值为"咽部充血V3"-"咽部充血V1"，如果"咽部充血V3"或"咽部充血V1"为空，则"d3delta"为空
    tab16_for1['d3delta'] = tab16_for1['咽部充血V3'] - tab16_for1['咽部充血V1']
    # tab16_for1增加一列”d4delta",值为"咽部充血V4"-"咽部充血V1"，如果"咽部充血V4"或"咽部充血V1"为空，则"d4delta"为空
    tab16_for1['d4delta'] = tab16_for1['咽部充血V4'] - tab16_for1['咽部充血V1']
    # 给tab16_6添加一列“疗效”，默认为nan
    tab16_for1['疗效'] = np.nan
    # 如果tab16_for1中的“d2delta”列的值为<0，但是'咽部充血V4'列的值不为1，则在tab16_for1中该行的“疗效”列中填入“改善”
    for idx in tab16_for1.index:
        if tab16_for1['d4delta'][idx] < 0 and tab16_for1['咽部充血V4'][idx] != 1:
            tab16_for1['疗效'][idx] = '改善'
    # 如果tab16_6中'咽部充血V4'列的值为1且"咽部充血V1"列的值大于1，则在tab16_for1中该行的“疗效”列中填入“治愈”
    for idx in tab16_for1.index:
        if tab16_for1['咽部充血V4'][idx] == 1 and tab16_for1['咽部充血V1'][idx] > 1:
            tab16_for1['疗效'][idx] = '治愈'
    # 如果tab16_6中的'咽部充血V4'列的值>'咽部充血V1'列的值并且'd4delta'列的值＞0，或'咽部充血V4'列的值=='咽部充血V1'列的值并且'd4delta'列的值==0，则在tab16_for1中该行的“疗效”列中填入“无效”    
    for idx in tab16_for1.index:
        if (tab16_for1['咽部充血V4'][idx] > tab16_for1['咽部充血V1'][idx] and tab16_for1['d4delta'][idx] > 0) or (tab16_for1['咽部充血V4'][idx] == tab16_for1['咽部充血V1'][idx] and tab16_for1['d4delta'][idx] == 0):
            tab16_for1['疗效'][idx] = '无效'

    # 将tab16_for1中疗效列的“改善”和“治愈”替换为“有效”，其余值替换为“无效”（不替换空值）
    tab16_for1['疗效'].replace(['改善', '治愈'], '有效', inplace=True)
    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值==”有效”的个数
    effective = tab16_for1[tab16_for1['疗效'] == '有效'].groupby('label').count()['疗效']
    # 根据tab16_6中的“label”列的值不同，计算“疗效”列中值！=”有效”的非空值个数
    ineffective = tab16_for1[tab16_for1['疗效'].notna() & (tab16_for1['疗效'] != '有效')].groupby('label').count()['疗效']
    # 根据tab16_for1中的“label”列的值不同，计算“疗效”列中的空值个数
    null_values = tab16_for1[tab16_for1['疗效'].isna()].groupby('label').size()
    # 将effective、ineffective、null_values合并为一个DataFrame
    tab16_result = pd.concat([effective, ineffective, null_values], axis=1)
    # 重命名列名
    tab16_result.columns = ['有效', '无效', '空值']
    # Calculate the total for each row (label) as the sum of '有效', '无效', and '空值'
    tab16_result['总数'] = tab16_result.sum(axis=1)
    # Calculate the proportion of '有效', '无效', and '空值' for each row (label) and convert it to percentage format
    tab16_result['有效比例'] = (tab16_result['有效'] / tab16_result['总数']).apply(lambda x: '{:.2%}'.format(x))
    tab16_result['无效比例'] = (tab16_result['无效'] / tab16_result['总数']).apply(lambda x: '{:.2%}'.format(x))
    tab16_result['空值比例'] = (tab16_result['空值'] / tab16_result['总数']).apply(lambda x: '{:.2%}'.format(x))
    # 使用卡方检验对比tab16_result_4中两行在“有效”和“无效”两列的卡方值和P值
    chi2, p, _, _ = stats.chi2_contingency(tab16_result[['有效', '无效']])

    # 在tab16_result_4中增加两个新列存储卡方值和P值
    tab16_result['卡方值'] = chi2
    tab16_result['P值'] = p
    
    st.markdown('## 咽部充血')
    st.write(tab16_result)



#%%

    tab16_for4_dict = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#咽部滤泡' in key:
            tab16_for4_dict[key] = tab16_dict[key]
    tab16_for4_columns = {}
    for key in tab16_for4_dict.keys():
        for column in tab16_for4_dict[key].columns:
            if '检查结果' in column:
                tab16_for4_columns[key] = tab16_for4_dict[key][['subject_id', column]]
    # 设置tab16_for1_columns中的每一个df的索引列为”subject_id“
    for key in tab16_for4_columns.keys():
        tab16_for4_columns[key].set_index('subject_id', inplace=True)
    # 将tab16_for4_columns中所有的df横向合并，索引列的值一一对应，得到一个新的df（tab16_for4）
    tab16_for4 = pd.concat(tab16_for4_columns.values(), axis=1)
    # 给tab16_for4中的每一列重命名，按照“检查结果V{i}”的格式
    tab16_for4.columns = [f'咽部滤泡V{i}' for i in range(1, len(tab16_for4.columns) + 1)]
    # 只保留咽部滤泡V1和咽部滤泡V4两列
    tab16_for4 = tab16_for4[['咽部滤泡V1', '咽部滤泡V4']]
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for4.index:
            tab16_for4.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for4.index:
            tab16_for4.loc[i, 'label'] = '对照组'
    
    # 只保留”咽部滤泡V1“列值为”有滤泡“的行
    tab16_for4 = tab16_for4[tab16_for4['咽部滤泡V1'] == '有滤泡']

    # 增加一列”疗效“
    tab16_for4['疗效'] = np.nan
    # 如果咽部

    
    st.write(tab16_for4)

    

    



#%%
    tab16_for2_dict = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#扁桃体肿大' in key:
            tab16_for2_dict[key] = tab16_dict[key]
    # 获取tab16_6_dict中每一个df包含字符串“检查结果”的列，并将这些列和当前df的”subject_id“列一起，添加到一个新的dict（tab16_for1_columns）中
    tab16_for2_columns = {}
    for key in tab16_for2_dict.keys():
        for column in tab16_for2_dict[key].columns:
            if '检查结果' in column:
                tab16_for2_columns[key] = tab16_for2_dict[key][['subject_id', column]]
    # 设置tab16_for2_columns中的每一个df的索引列为”subject_id“
    for key in tab16_for2_columns.keys():
        tab16_for2_columns[key].set_index('subject_id', inplace=True)
    # 将tab16_for2_columns中所有的df横向合并，索引列的值一一对应，得到一个新的df（tab16_for2）
    tab16_for2 = pd.concat(tab16_for2_columns.values(), axis=1)
    # 合并后将列名重命名为“扁桃体肿大V1”，“扁桃体肿大V2”，"扁桃体肿大V3","扁桃体肿大V4“,"扁桃体肿大V5"，“扁桃体肿大V6"
    tab16_for2.columns = ['扁桃体肿大V1', '扁桃体肿大V2', '扁桃体肿大V3', '扁桃体肿大V4', '扁桃体肿大V5', '扁桃体肿大V6']
    match = pd.read_excel('match.xlsx')
    # 遍历tab16_6的索引列，并将其中每一个值与match中的“index”进行比较
    # 如果match中的”index“列的值不存在与tab16_6索引列中，则将match中的”index“列的值添加到tab16_6中df的索引列中，对应行中其他列的值为nan
    for index in match['index']:
        if index not in tab16_for2.index:
            tab16_for2.loc[index] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    # tab16_6中添加一列“label”
    tab16_for2['label'] = np.nan
    # 如果tab16_6中的subject_id列的值出现在dlct的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"试验组"
    for index in dlct['index']:
        if index in tab16_for2.index:
            tab16_for2['label'][index] = '试验组'
    # 如果tab16_6中的subject_id列的值出现在dlcc的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"对照组"
    for index in dlcc['index']:
        if index in tab16_for2.index:
            tab16_for2['label'][index] = '对照组'
    
    # 如果tab16_for2中'扁桃体肿大V1'列的值为”无肿大“，则删除对应的行
    tab16_for2.drop(tab16_for2[tab16_for2['扁桃体肿大V1'] == '无肿大'].index, inplace=True)

    for column in tab16_for2.columns:
        for idx in tab16_for2.index:
            value = tab16_for2.loc[idx, column]
            if value == '无肿大':
                # 如果tab16_for2中的某一行的某一列的值为”无肿大“，则将该值改为0
                tab16_for2.loc[idx, column] = 0
            # 如果值为nan，则该值不变
            elif pd.isnull(value):
                continue
            # 如果tab16_for2中的某一行的某一列的值中包含字符串“Ⅰ度”，则将该值改为1
            elif 'Ⅰ度' in value:
                tab16_for2.loc[idx, column] = 1
            # 如果tab16_for2中的某一行的某一列的值中包含字符串“Ⅱ度”，则将该值改为2
            elif 'Ⅱ度' in value:
                tab16_for2.loc[idx, column] = 2
            # 如果tab16_for2中的某一行的某一列的值中包含字符串“Ⅲ度”，则将该值改为3
            elif 'Ⅲ度' in value:
                tab16_for2.loc[idx, column] = 3
    
    # tab16_for2增加一列”delta“，delta列的值 = 扁桃体肿大V4 - 扁桃体肿大V1
    tab16_for2['delta'] = tab16_for2['扁桃体肿大V4'] - tab16_for2['扁桃体肿大V1']

    # tab16_for2增加一列”疗效“，如果delta列的值为0，则疗效列的值为”无效“
    tab16_for2['疗效'] = np.nan
    tab16_for2.loc[tab16_for2['delta'] == 0, '疗效'] = '无效'
    # 如果delta列的值小于0，则疗效列的值为”有效“
    tab16_for2.loc[tab16_for2['delta'] < 0, '疗效'] = '有效'

    # 根据label列的值不同，统计疗效列中不同值的个数和占比，存入一个df名为result
    result = pd.DataFrame()
    result['试验组'] = tab16_for2[tab16_for2['label'] == '试验组']['疗效'].value_counts()
    result['试验组占比'] = result['试验组'] / result['试验组'].sum()
    result['对照组'] = tab16_for2[tab16_for2['label'] == '对照组']['疗效'].value_counts()
    result['对照组占比'] = result['对照组'] / result['对照组'].sum()
    result['试验组空值'] = tab16_for2[(tab16_for2['label'] == '试验组') & (tab16_for2['疗效'].isna())].shape[0]
    result['对照组空值'] = tab16_for2[(tab16_for2['label'] == '对照组') & (tab16_for2['疗效'].isna())].shape[0]
    # Extract the '有效' and '无效' rows from the 'result' DataFrame
    valid_rows = result.loc[['有效', '无效'], ['试验组', '对照组']]
    # Create a new DataFrame 'df' to store the four-grid table
    df = pd.DataFrame(valid_rows)
    df = df.T
    # 使用卡方检验对比df中两行在“有效”和“无效”两列的卡方值和P值
    chi2, p, _, _ = stats.chi2_contingency(df[['有效', '无效']])
    # 在result中增加两个新列存储卡方值和P值
    result['卡方值'] = chi2
    result['P值'] = p
    st.write('## 扁桃体肿大')
    st.write(result)
    

#%%
    tab16_for3_dict = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for3_dict[key] = tab16_dict[key]
    tab16_for3_col_dict = {}
    # 遍历tab16_dict_self中的每一个df
    for sheet in tab16_for3_dict.keys():
        # 获取当前df中列名中包含字符串”声音嘶哑“的列,和df中的subject_id列一起，存入字典中
        tab16_for3_col_dict[sheet] = tab16_for3_dict[sheet][['subject_id'] + [col for col in tab16_for3_dict[sheet].columns if '声音嘶哑' in col]]

    # 设置tab16_for3_col_dict中的每一个df的索引为subject_id
    for key in tab16_for3_col_dict.keys():
        tab16_for3_col_dict[key].set_index('subject_id', inplace=True)
    # 将字典中的df合并为一个df，按照索引一一对应
    tab16_for3 = pd.concat(tab16_for3_col_dict.values(), axis=1)
    # 重新整理tab16_for3的列名为”声音嘶哑V{i}“
    tab16_for3.columns = ['声音嘶哑V' + str(i) for i in range(1, tab16_for3.shape[1] + 1)]
    # 如果tab16_6的值中包括字符串“分”，则删掉这个字符串
    tab16_for3 = tab16_for3.replace('分', '', regex=True)
    # 将tab16_6中的值转换为float类型
    tab16_for3 = tab16_for3.astype(float)
    for column in tab16_for3.columns:
        for idx in tab16_for3.index:
            value = tab16_for3.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for3.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for3.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for3.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for3.loc[idx, column] = 1
    # tab16_6中添加一列“label”
    tab16_for3['label'] = np.nan
    # 如果tab16_6中的subject_id列的值出现在dlct的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"试验组"
    for index in dlct['index']:
        if index in tab16_for3.index:
            tab16_for3['label'][index] = '试验组'
    # 如果tab16_6中的subject_id列的值出现在dlcc的列名为"index"的列中，则在tab16_6中该subject_id对应的行的label列中填入"对照组"
    for index in dlcc['index']:
        if index in tab16_for3.index:
            tab16_for3['label'][index] = '对照组'

    # tab16_6增加一列”d2delta",值为"咽部疼痛D2"-"咽部疼痛D1"，如果"咽部疼痛D2"或"咽部疼痛D1"为空，则"d2delta"为空
    tab16_for3['d2delta'] = tab16_for3['声音嘶哑V2'] - tab16_for3['声音嘶哑V1']
    # tab16_6增加一列”d3delta",值为"咽部疼痛D3"-"咽部疼痛D1"，如果"咽部疼痛D3"或"咽部疼痛D1"为空，则"d3delta"为空
    tab16_for3['d3delta'] = tab16_for3['声音嘶哑V3'] - tab16_for3['声音嘶哑V1']
    # tab16_6增加一列”d4delta",值为"咽部疼痛D4"-"咽部疼痛D1"，如果"咽部疼痛D4"或"咽部疼痛D1"为空，则"d4delta"为空
    tab16_for3['d4delta'] = tab16_for3['声音嘶哑V4'] - tab16_for3['声音嘶哑V1']
    # 给tab16_6添加一列“疗效”，默认为nan
    tab16_for3['疗效'] = np.nan
    # 如果tab16_for3中的“d2delta”列的值为<0，但是'声音嘶哑V4'列的值不为1，则在tab16_for3中该行的“疗效”列中填入“改善”
    for idx in tab16_for3.index:
        if tab16_for3['d2delta'][idx] < 0 and tab16_for3['声音嘶哑V4'][idx] != 1:
            tab16_for3['疗效'][idx] = '改善'
    # 如果如果tab16_for3中'声音嘶哑V4'列的值为1，且”声音嘶哑V1"列的值不为1，则在tab16_for3中该行的“疗效”列中填入“治愈”
    for idx in tab16_for3.index:
        if tab16_for3['声音嘶哑V4'][idx] == 1 and tab16_for3['声音嘶哑V1'][idx] != 1:
            tab16_for3['疗效'][idx] = '治愈'
    # 如果tab16_for3中的'声音嘶哑V4'列的值>'声音嘶哑V1'列的值并且'd4delta'列的值＞0，或'声音嘶哑V4'列的值=='声音嘶哑V1'列的值并且'd4delta'列的值==0，则在tab16_for3中该行的“疗效”列中填入“无效”
    for idx in tab16_for3.index:
        if (tab16_for3['声音嘶哑V4'][idx] > tab16_for3['声音嘶哑V1'][idx] and tab16_for3['d4delta'][idx] > 0) or (tab16_for3['声音嘶哑V4'][idx] == tab16_for3['声音嘶哑V1'][idx] and tab16_for3['d4delta'][idx] == 0):
            tab16_for3['疗效'][idx] = '无效'

    
    # 将tab16_for3中疗效列的“改善”和“治愈”替换为“有效”，其余值替换为“无效”（不替换空值）
    tab16_for3['疗效'].replace(['改善', '治愈'], '有效', inplace=True)
    # 根据tab16_for3中的“label”列的值不同，计算“疗效”列中值==”有效”的个数
    effective = tab16_for3[tab16_for3['疗效'] == '有效'].groupby('label').count()['疗效']
    # 根据tab16_for3中的“label”列的值不同，计算“疗效”列中值！=”有效”的非空值个数
    ineffective = tab16_for3[tab16_for3['疗效'].notna() & (tab16_for3['疗效'] != '有效')].groupby('label').count()['疗效']
    # 根据tab16_for3中的“label”列的值不同，计算“疗效”列中的空值个数
    null_values = tab16_for3[tab16_for3['疗效'].isna()].groupby('label').size()
    # 将effective、ineffective、null_values合并为一个DataFrame
    tab16_result_4 = pd.concat([effective, ineffective, null_values], axis=1)
    # 重命名列名
    tab16_result_4.columns = ['有效', '无效', '空值']

    # Calculate the total for each row (label) as the sum of '有效', '无效', and '空值'
    tab16_result_4['总数'] = tab16_result_4.sum(axis=1)
    # Calculate the proportion of '有效', '无效', and '空值' for each row (label) and convert it to percentage format
    tab16_result_4['有效比例'] = (tab16_result_4['有效'] / tab16_result_4['总数']).apply(lambda x: '{:.2%}'.format(x))
    tab16_result_4['无效比例'] = (tab16_result_4['无效'] / tab16_result_4['总数']).apply(lambda x: '{:.2%}'.format(x))
    tab16_result_4['空值比例'] = (tab16_result_4['空值'] / tab16_result_4['总数']).apply(lambda x: '{:.2%}'.format(x))
    

    # 使用卡方检验对比tab16_result_4中两行在“有效”和“无效”两列的卡方值和P值
    chi2, p, _, _ = stats.chi2_contingency(tab16_result_4[['有效', '无效']])

    # 在tab16_result_4中增加两个新列存储卡方值和P值
    tab16_result_4['卡方值'] = chi2
    tab16_result_4['P值'] = p
    
    st.markdown('## 声音嘶哑')
    st.write(tab16_result_4)
    
        

     


    

    




    


