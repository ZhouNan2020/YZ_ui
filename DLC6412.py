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
    
    # 根据label列的值不同，分别统计tab16_for1中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for1_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for1_noncount.loc['delta_D1'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D2'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D3'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D4'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D5'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D6'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for1_noncount.loc['delta_D7'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for1_noncount.loc['delta_研究完成'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for1_noncount.loc['delta_计划外'] = [tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for1_df.loc[tab16_for1_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for1_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for1_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for1_noncount = tab16_for1_noncount.T
    
    st.write(tab16_for1_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for1_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for1_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for1_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    # 根据label列的值不同，分别统计tab16_for1中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    # 根据label列的值不同，分别统计tab16_for1中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for1_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for1_df.loc[(tab16_for1_df['label'] == '试验组') & (tab16_for1_df[column] == '治愈'), column].count()
        valid_trial = tab16_for1_df.loc[(tab16_for1_df['label'] == '试验组') & (tab16_for1_df[column] == '有效'), column].count()
        invalid_trial = tab16_for1_df.loc[(tab16_for1_df['label'] == '试验组') & (tab16_for1_df[column] == '无效'), column].count()
        cure_control = tab16_for1_df.loc[(tab16_for1_df['label'] == '对照组') & (tab16_for1_df[column] == '治愈'), column].count()
        valid_control = tab16_for1_df.loc[(tab16_for1_df['label'] == '对照组') & (tab16_for1_df[column] == '有效'), column].count()
        invalid_control = tab16_for1_df.loc[(tab16_for1_df['label'] == '对照组') & (tab16_for1_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for1_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for1_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for1_count = tab16_for1_count.T
    st.write(tab16_for1_count)
    # 对tab16_for1_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for1_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for1_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    
    st.markdown('## 2.咽痒')

    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '为间歇转持续痒' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '为间歇转持续痒' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
        # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')

    
    
    st.markdown('## 3.恶心')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '因恶心而卧床' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '因恶心而卧床' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
    # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')

    
    
    
    st.markdown('## 4.粘痰')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '痰液黏稠指清痰' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '痰液黏稠指清痰' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 0) & (tab16_for2_df['患者自评D1'] == 0), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
    # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')

   
    
    st.markdown('## 5.食欲不振')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '进食50%～75%原进食量' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '进食50%～75%原进食量' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
        
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
        # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')

  

    
    
    st.markdown('## 6.发热')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '无发热（腋温）' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '无发热（腋温）' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
        # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
        
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')



    
    st.markdown('## 7.咳嗽')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '咳嗽较频繁' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '咳嗽较频繁' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
    # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')



    st.markdown('## 8.耳痛')
    tab16_for2_dict_1 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '患者自评（' in key:
            tab16_for2_dict_1[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    keys_list = list(tab16_for2_dict_1.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if 'D1' in key:
            tab16_for2_dict_1['D1'] = tab16_for2_dict_1.pop(key)
        elif 'D3' in key:
            tab16_for2_dict_1['D3'] = tab16_for2_dict_1.pop(key)
        elif 'D5' in key:
            tab16_for2_dict_1['D5'] = tab16_for2_dict_1.pop(key)
        elif 'D6' in key:
            tab16_for2_dict_1['D6'] = tab16_for2_dict_1.pop(key)
    tab16_for2_dict_2 = {}
    for key in tab16_dict.keys():
        # 包括字符串“#患者自评”但是不包括字符串“患者自评（”的key
        if '#患者自评' in key and '患者自评（' not in key:
            tab16_for2_dict_2[key] = tab16_dict[key]
    # 重命名tab16_for2_dict_1中的每一个key的名字为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”
    keys_list = list(tab16_for2_dict_2.keys())
    for key in keys_list:
        # 如果key中有字符串”访视1“
        if '访视1' in key:
            tab16_for2_dict_2['D0'] = tab16_for2_dict_2.pop(key)
        elif '访视2' in key:
            tab16_for2_dict_2['D2'] = tab16_for2_dict_2.pop(key)
        elif '访视3' in key:
            tab16_for2_dict_2['D4'] = tab16_for2_dict_2.pop(key)
        elif '访视4' in key:
            tab16_for2_dict_2['D7'] = tab16_for2_dict_2.pop(key)
        elif '研究完成' in key:
            tab16_for2_dict_2['研究完成'] = tab16_for2_dict_2.pop(key)
        elif '计划外' in key:
            tab16_for2_dict_2['计划外'] = tab16_for2_dict_2.pop(key)
    # tab16_for2_dict_1中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_1.keys():
        columns_to_keep = [col for col in tab16_for2_dict_1[key].columns if '耳痛' in col] + ['subject_id']
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key][columns_to_keep]
    # tab16_for2_dict_2中每个df只保留包含字符串”咽干口微渴“的列和subject_id列
    for key in tab16_for2_dict_2.keys():
        columns_to_keep = [col for col in tab16_for2_dict_2[key].columns if '耳痛' in col] + ['subject_id']
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key][columns_to_keep]
    # tab16_for2_dict_1中每个df设置subject_id列为索引
    for key in tab16_for2_dict_1.keys():
        tab16_for2_dict_1[key] = tab16_for2_dict_1[key].set_index('subject_id')
    # tab16_for2_dict_2中每个df设置subject_id列为索引
    for key in tab16_for2_dict_2.keys():
        tab16_for2_dict_2[key] = tab16_for2_dict_2[key].set_index('subject_id')
    # 将tab16_for2_dict_1中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_1 = pd.concat(tab16_for2_dict_1, axis=1)
    # 将tab16_for2_dict_2中的每一个df横向合并，按照索引一一对应关系合并
    tab16_for2_df_2 = pd.concat(tab16_for2_dict_2, axis=1)
    # 重命名tab16_for2_df_1的列名为“患者自评D1”，“患者自评D3”，“患者自评D5”，“患者自评D6”
    tab16_for2_df_1.columns = ['患者自评D1', '患者自评D3', '患者自评D5', '患者自评D6']
    # 重命名tab16_for2_df_2的列名为“患者自评D0”，“患者自评D2”，“患者自评D4”，“患者自评D7”，“患者自评_研究完成”，“患者自评_计划外”
    tab16_for2_df_2.columns = ['患者自评D0', '患者自评D2', '患者自评D4', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']
    # 将tab16_for2_df_1和tab16_for2_df_2按照索引横向合并
    tab16_for2_df = pd.concat([tab16_for2_df_1, tab16_for2_df_2], axis=1)
    # 重新按照访视顺序排列列名
    tab16_for2_df = tab16_for2_df[['患者自评D0', '患者自评D1', '患者自评D2', '患者自评D3', '患者自评D4', '患者自评D5', '患者自评D6', '患者自评D7', '患者自评_研究完成', '患者自评_计划外']]
    
    for column in tab16_for2_df.columns:
        for idx in tab16_for2_df.index:
            value = tab16_for2_df.loc[idx, column]
            # 如果值为nan，则跳过
            if np.isnan(value):
                pass
            # 如果7<=值<=10，则替换为4
            elif 7 <= value <= 10.0:
                tab16_for2_df.loc[idx, column] = 4
            # 如果4<=值<=6，则替换为3
            elif 4 <= value <= 6.0:
                tab16_for2_df.loc[idx, column] = 3
            # 如果1<=值<=3，则替换为2
            elif 1 <= value <= 3.0:
                tab16_for2_df.loc[idx, column] = 2
            # 如果值=0，则替换为1
            elif value == 0:
                tab16_for2_df.loc[idx, column] = 1
    
    # delta_D1 = 患者自评D1 - 患者自评D0
    tab16_for2_df['delta_D1'] = tab16_for2_df['患者自评D1'] - tab16_for2_df['患者自评D0']
    # delta_D2 = 患者自评D2 - 患者自评D0
    tab16_for2_df['delta_D2'] = tab16_for2_df['患者自评D2'] - tab16_for2_df['患者自评D0']
    # delta_D3 = 患者自评D3 - 患者自评D0
    tab16_for2_df['delta_D3'] = tab16_for2_df['患者自评D3'] - tab16_for2_df['患者自评D0']
    # delta_D4 = 患者自评D4 - 患者自评D0
    tab16_for2_df['delta_D4'] = tab16_for2_df['患者自评D4'] - tab16_for2_df['患者自评D0']
    # delta_D5 = 患者自评D5 - 患者自评D0
    tab16_for2_df['delta_D5'] = tab16_for2_df['患者自评D5'] - tab16_for2_df['患者自评D0']
    # delta_D6 = 患者自评D6 - 患者自评D0
    tab16_for2_df['delta_D6'] = tab16_for2_df['患者自评D6'] - tab16_for2_df['患者自评D0']
    # delta_D7 = 患者自评D7 - 患者自评D0
    tab16_for2_df['delta_D7'] = tab16_for2_df['患者自评D7'] - tab16_for2_df['患者自评D0']
    # delta_研究完成 = 患者自评_研究完成 - 患者自评D0
    tab16_for2_df['delta_研究完成'] = tab16_for2_df['患者自评_研究完成'] - tab16_for2_df['患者自评D0']
    # delta_计划外 = 患者自评_计划外 - 患者自评D0
    tab16_for2_df['delta_计划外'] = tab16_for2_df['患者自评_计划外'] - tab16_for2_df['患者自评D0']
    
    # 如果患者自评D0!=1,且delta_D1<0,则delta_D1值更改为”有效“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D1'] < 0), 'delta_D1'] = '有效'
    # 如果患者自评D0!=0,且患者自评D1==0,则delta_D1值更改为”治愈“
    tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D1'] == 1), 'delta_D1'] = '治愈'
    # delta_D1 中除了”有效“，”治愈“和np.nan外的值都更改为”无效“
    tab16_for2_df.loc[(tab16_for2_df['delta_D1'] != '有效') & (tab16_for2_df['delta_D1'] != '治愈') & (tab16_for2_df['delta_D1'].notna()), 'delta_D1'] = '无效'
    
    # 对于D2到D7，研究完成，计划外，按照D1的规则进行更改
    for i in range(2, 8):
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_D'+str(i)] < 0), 'delta_D'+str(i)] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评D'+str(i)] == 1), 'delta_D'+str(i)] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_D'+str(i)] != '有效') & (tab16_for2_df['delta_D'+str(i)] != '治愈') & (tab16_for2_df['delta_D'+str(i)].notna()), 'delta_D'+str(i)] = '无效'
    
    for column in ['研究完成', '计划外']:
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['delta_'+column] < 0), 'delta_'+column] = '有效'
        tab16_for2_df.loc[(tab16_for2_df['患者自评D0'] != 1) & (tab16_for2_df['患者自评_'+column] == 1), 'delta_'+column] = '治愈'
        tab16_for2_df.loc[(tab16_for2_df['delta_'+column] != '有效') & (tab16_for2_df['delta_'+column] != '治愈') & (tab16_for2_df['delta_'+column].notna()), 'delta_'+column] = '无效'
    # tab16_for2_df增加一列”label“，值默认为nan
    tab16_for2_df['label'] = np.nan
    # 遍历dlct的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”试验组“
    for i in dlct['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '试验组'
    # 遍历dlcc的"index"列，如果其中的值出现在tab16_for2_df的索引中，则tab16_for2_df中该行对应的label列填入”对照组“
    for i in dlcc['index']:
        if i in tab16_for2_df.index:
            tab16_for2_df.loc[i, 'label'] = '对照组'

    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列的空值计数和非空值计数，将其存为一个新的df
    tab16_for2_noncount = pd.DataFrame(columns=['试验组空值计数', '试验组非空值计数', '对照组空值计数', '对照组非空值计数'])
    tab16_for2_noncount.loc['delta_D1'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D1'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D1'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D2'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D2'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D2'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D3'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D3'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D3'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D4'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D4'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D4'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D5'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D5'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D5'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D6'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D6'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D6'].notnull().sum()]
    tab16_for2_noncount.loc['delta_D7'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_D7'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_D7'].notnull().sum()]
    tab16_for2_noncount.loc['delta_研究完成'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_研究完成'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_研究完成'].notnull().sum()]
    tab16_for2_noncount.loc['delta_计划外'] = [tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '试验组', 'delta_计划外'].notnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].isnull().sum(),
                                        tab16_for2_df.loc[tab16_for2_df['label'] == '对照组', 'delta_计划外'].notnull().sum()]
    # 将tab16_for2_noncount的前7个索引修改为”第1天“，”第2天“，”第3天“，”第4天“，”第5天“，”第6天“，”第7天“
    tab16_for2_noncount.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    # 转置
    tab16_for2_noncount = tab16_for2_noncount.T
    st.write(tab16_for2_noncount)
    from scipy.stats import chi2_contingency
    # 对tab16_for2_noncount中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_noncount.columns:
        # 形成四格表
        contingency_table = tab16_for2_noncount[[column]].values.reshape(2, 2)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
    
    
    # 根据label列的值不同，分别统计tab16_for2中从delta_D1列到delta_计划外列中不同值的计数（不包括空值），将其存为一个新的df
    delta_columns = ['delta_D1', 'delta_D2', 'delta_D3', 'delta_D4', 'delta_D5', 'delta_D6', 'delta_D7', 'delta_研究完成', 'delta_计划外']
    tab16_for2_count = pd.DataFrame(columns=['试验组治愈计数', '试验组有效计数', '试验组无效计数', '对照组治愈计数', '对照组有效计数', '对照组无效计数', '试验组治愈占比', '试验组有效占比', '试验组无效占比', '对照组治愈占比', '对照组有效占比', '对照组无效占比'])
    for column in delta_columns:
        cure_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_trial = tab16_for2_df.loc[(tab16_for2_df['label'] == '试验组') & (tab16_for2_df[column] == '无效'), column].count()
        cure_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '治愈'), column].count()
        valid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '有效'), column].count()
        invalid_control = tab16_for2_df.loc[(tab16_for2_df['label'] == '对照组') & (tab16_for2_df[column] == '无效'), column].count()
        total_trial = cure_trial + valid_trial + invalid_trial
        total_control = cure_control + valid_control + invalid_control
        tab16_for2_count.loc[column] = [cure_trial, valid_trial, invalid_trial, cure_control, valid_control, invalid_control, cure_trial/total_trial, valid_trial/total_trial, invalid_trial/total_trial, cure_control/total_control, valid_control/total_control, invalid_control/total_control]
    tab16_for2_count.index = ['第1天','第2天','第3天','第4天','第5天','第6天','第7天','研究完成','计划外']
    tab16_for2_count = tab16_for2_count.T
    st.write(tab16_for2_count)
    # 对tab16_for2_count中每一列进行卡方检验
    st.write('#### 对于以上表的卡方检验结果如下：')
    for column in tab16_for2_count.columns:
        # 只使用每一列的前6行形成四格表
        contingency_table = tab16_for2_count[[column]].values[:6].reshape(2, 3)
        # 尝试进行卡方检验
        try:
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            # 输出卡方检验结果
            st.write(f'对于{column}，卡方值为{chi2}，p值为{p}')
        except ValueError:
            st.write(f'对于{column}，无法进行卡方检验，因为期望频数表中存在零元素')
