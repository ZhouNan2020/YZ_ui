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
    

    # 获取tab16_dict中的“访视1筛选-基线（0天）#96609#生命体征”，“访视4研究第7天 #96675#生命体征","研究完成访视#96676#生命体征"三个key对应的df，存入一个新的dict中
    tab16_dict_1 = {}
    for sheet in tab16_dict.keys():
        if sheet in ["访视1筛选-基线（0天）#96609#生命体征", "访视4研究第7天 #96675#生命体征", "研究完成访视#96676#生命体征"]:
            tab16_dict_1[sheet] = tab16_dict[sheet]
    # 计算tab16_dict_1中的每一个df中的”体温“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict = {}
    for key, df in tab16_dict_1.items():
        df['体温'] = pd.to_numeric(df['体温'], errors='coerce')
        grouped = df.groupby('label')['体温']
        stats_df = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result = stats.ttest_ind(df[df['label'] == '试验组']['体温'].dropna(), df[df['label'] == '对照组']['体温'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df['检验方法'] = 't检验'
        stats_df['统计量'] = t_test_result.statistic
        stats_df['p值'] = t_test_result.pvalue
        stats_dict[key] = stats_df
    # 遍历stats_dict中的每一个key使用st.write显示
    st.markdown('## 体温')
    for key in stats_dict.keys():
        st.write(key)
        st.write(stats_dict[key])

    # 计算tab16_dict_1中的每一个df中的”心率“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值

    # 计算tab16_dict_1中的每一个df中的”心率“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict_1 = {}
    for key, df in tab16_dict_1.items():
        df['心率'] = pd.to_numeric(df['心率'], errors='coerce')
        grouped = df.groupby('label')['心率']
        stats_df_1 = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result_1 = stats.ttest_ind(df[df['label'] == '试验组']['心率'].dropna(), df[df['label'] == '对照组']['心率'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df_1['检验方法'] = 't检验'
        stats_df_1['统计量'] = t_test_result_1.statistic
        stats_df_1['p值'] = t_test_result_1.pvalue
        stats_dict_1[key] = stats_df_1
    # 遍历stats_dict_1中的每一个key使用st.write显示
    st.markdown('## 心率')
    for key in stats_dict_1.keys():
        st.write(key)
        st.write(stats_dict_1[key])


    
    # 计算tab16_dict_1中的每一个df中的”脉搏“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict_2 = {}
    for key, df in tab16_dict_1.items():
        df['脉率'] = pd.to_numeric(df['脉率'], errors='coerce')
        grouped = df.groupby('label')['脉率']
        stats_df_2 = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result_2 = stats.ttest_ind(df[df['label'] == '试验组']['脉率'].dropna(), df[df['label'] == '对照组']['脉率'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df_2['检验方法'] = 't检验'
        stats_df_2['统计量'] = t_test_result_2.statistic
        stats_df_2['p值'] = t_test_result_2.pvalue
        stats_dict_2[key] = stats_df_2
    # 遍历stats_dict_2中的每一个key使用st.write显示
    st.markdown('## 脉率')
    for key in stats_dict_2.keys():
        st.write(key)
        st.write(stats_dict_2[key])


    
    # 计算tab16_dict_1中的每一个df中的”呼吸“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict_3 = {}
    for key, df in tab16_dict_1.items():
        df['呼吸'] = pd.to_numeric(df['呼吸'], errors='coerce')
        grouped = df.groupby('label')['呼吸']
        stats_df_3 = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result_3 = stats.ttest_ind(df[df['label'] == '试验组']['呼吸'].dropna(), df[df['label'] == '对照组']['呼吸'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df_3['检验方法'] = 't检验'
        stats_df_3['统计量'] = t_test_result_3.statistic
        stats_df_3['p值'] = t_test_result_3.pvalue
        stats_dict_3[key] = stats_df_3
    # 遍历stats_dict_3中的每一个key使用st.write显示
    st.markdown('## 呼吸')
    for key in stats_dict_3.keys():
        st.write(key)
        st.write(stats_dict_3[key])


    
    # 计算tab16_dict_1中的每一个df中的”收缩压“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict_4 = {}
    for key, df in tab16_dict_1.items():
        df['收缩压'] = pd.to_numeric(df['收缩压'], errors='coerce')
        grouped = df.groupby('label')['收缩压']
        stats_df_4 = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result_4 = stats.ttest_ind(df[df['label'] == '试验组']['收缩压'].dropna(), df[df['label'] == '对照组']['收缩压'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df_4['检验方法'] = 't检验'
        stats_df_4['统计量'] = t_test_result_4.statistic
        stats_df_4['p值'] = t_test_result_4.pvalue
        stats_dict_4[key] = stats_df_4
    # 遍历stats_dict_4中的每一个key使用st.write显示
    st.markdown('## 收缩压')
    for key in stats_dict_4.keys():
        st.write(key)
        st.write(stats_dict_4[key])


    
    # 计算tab16_dict_1中的每一个df中的”舒张压“列的非空值计数、空值计数，均值，标准差，中位数，Q1，Q3，最小值，最大值，这些统计量形成一个df，df名称为tab16_dict_1中的key名，存于一个新的dict中
    # 根据“label”列值的不同，使用t检验对比不同组的差异，在stats_df中继续填入“检验方法”，“统计量”和“p值”，“检验方法”为“t检验",统计量为t值，p值为p值
    stats_dict_5 = {}
    for key, df in tab16_dict_1.items():
        df['舒张压'] = pd.to_numeric(df['舒张压'], errors='coerce')
        grouped = df.groupby('label')['舒张压']
        stats_df_5 = pd.DataFrame({
            '非空值计数': grouped.count(),
            '空值计数': grouped.apply(lambda x: x.isnull().sum()),
            '均值': grouped.mean(),
            '标准差': grouped.std(),
            '中位数': grouped.median(),
            'Q1': grouped.quantile(0.25),
            'Q3': grouped.quantile(0.75),
            '最小值': grouped.min(),
            '最大值': grouped.max()
        })
        # 使用t检验对比不同组的差异
        t_test_result_5 = stats.ttest_ind(df[df['label'] == '试验组']['舒张压'].dropna(), df[df['label'] == '对照组']['舒张压'].dropna())
        # 在stats_df中填入“检验方法”，“统计量”和“p值”
        stats_df_5['检验方法'] = 't检验'
        stats_df_5['统计量'] = t_test_result_5.statistic
        stats_df_5['p值'] = t_test_result_5.pvalue
        stats_dict_5[key] = stats_df_5
    # 遍历stats_dict_5中的每一个key使用st.write显示
    st.markdown('## 舒张压')
    for key in stats_dict_5.keys():
        st.write(key)
        st.write(stats_dict_5[key])




    # 获取tab16_dict中的“"访视1筛选-基线（0天）#96610#体格检查""对应的df
    df_1 = tab16_dict["访视1筛选-基线（0天）#96610#体格检查"]
    # 根据df_1中label列的值不同，分组统计df_1中”1.一般状况“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 一般状况')
    # 根据df_1中label列的值不同，分组统计df_1中”1.一般状况“列中非空值的计数和空值计数
    grouped_1 = df_1.groupby('label')['1.一般状况']
    stats_df_1 = pd.DataFrame({
        '非空值计数': grouped_1.apply(lambda x: x.count()),
        '空值计数': grouped_1.apply(lambda x: x.isnull().sum())
    })
    # 尝试进行卡方检验，如果不满足卡方检验条件则跳过，并st.write('不适合进行卡方检验')
    try:
        chi2_test_result = stats.chi2_contingency([stats_df_1.loc['试验组'], stats_df_1.loc['对照组']])
        stats_df_1['检验方法'] = '卡方检验'
        stats_df_1['统计量'] = chi2_test_result[0]
        stats_df_1['p值'] = chi2_test_result[1]
    except ValueError:
        st.write('不适合进行卡方检验')
        stats_df_1['检验方法'] = 'N/A'
        stats_df_1['统计量'] = 'N/A'
        stats_df_1['p值'] = 'N/A'
        
    value_counts = grouped_1.value_counts().unstack().fillna(0)
    
    # 尝试进行卡方检验，如果不满足卡方检验条件则跳过，并st.write('不适合进行卡方检验')
    try:
        chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
        value_counts['检验方法'] = '卡方检验'
        value_counts['统计量'] = chi2_test_result[0]
        value_counts['p值'] = chi2_test_result[1]
    except ValueError:
        st.write('不适合进行卡方检验')
        value_counts['检验方法'] = 'N/A'
        value_counts['统计量'] = 'N/A'
        value_counts['p值'] = 'N/A'
        
    value_counts_percent = grouped_1.value_counts(normalize=True).unstack().fillna(0) * 100
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_1_1
    stats_df_1_1 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_1)
    st.write(stats_df_1_1)


    # 根据df_1中label列的值不同，分组统计df_1中”2.头颈部“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 头颈部')
    # 根据df_1中label列的值不同，分组统计df_1中”2.头颈部“列中非空值的计数和空值计数
    grouped_2 = df_1.groupby('label')['2.头颈部']
    stats_df_2 = pd.DataFrame({
        '非空值计数': grouped_2.apply(lambda x: x.count()),
        '空值计数': grouped_2.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_2.loc['试验组'], stats_df_2.loc['对照组']])
    # 在stats_df_2中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_2['检验方法'] = '卡方检验'
    stats_df_2['统计量'] = chi2_test_result[0]
    stats_df_2['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”2.头颈部“列中不同值的计数和占比
    value_counts = grouped_2.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_2.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_2_2
    stats_df_2_2 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_2)
    st.write(stats_df_2_2)


    # 根据df_1中label列的值不同，分组统计df_1中”3.皮肤“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 皮肤')
    # 根据df_1中label列的值不同，分组统计df_1中”3.皮肤“列中非空值的计数和空值计数
    grouped_3 = df_1.groupby('label')['3.皮肤']
    stats_df_3 = pd.DataFrame({
        '非空值计数': grouped_3.apply(lambda x: x.count()),
        '空值计数': grouped_3.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_3.loc['试验组'], stats_df_3.loc['对照组']])
    # 在stats_df_3中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_3['检验方法'] = '卡方检验'
    stats_df_3['统计量'] = chi2_test_result[0]
    stats_df_3['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”3.皮肤“列中不同值的计数和占比
    value_counts = grouped_3.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_3.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_3_3
    stats_df_3_3 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_3)
    st.write(stats_df_3_3)

    # 根据df_1中label列的值不同，分组统计df_1中”4.黏膜“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 黏膜')
    # 根据df_1中label列的值不同，分组统计df_1中”4.黏膜“列中非空值的计数和空值计数
    grouped_4 = df_1.groupby('label')['4.黏膜']
    stats_df_4 = pd.DataFrame({
        '非空值计数': grouped_4.apply(lambda x: x.count()),
        '空值计数': grouped_4.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_4.loc['试验组'], stats_df_4.loc['对照组']])
    # 在stats_df_4中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_4['检验方法'] = '卡方检验'
    stats_df_4['统计量'] = chi2_test_result[0]
    stats_df_4['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”4.黏膜“列中不同值的计数和占比
    value_counts = grouped_4.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_4.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_4_4
    stats_df_4_4 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_4)
    st.write(stats_df_4_4)

    # 根据df_1中label列的值不同，分组统计df_1中”5.浅表淋巴结“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 浅表淋巴结')
    # 根据df_1中label列的值不同，分组统计df_1中”5.浅表淋巴结“列中非空值的计数和空值计数
    grouped_5 = df_1.groupby('label')['5.浅表淋巴结']
    stats_df_5 = pd.DataFrame({
        '非空值计数': grouped_5.apply(lambda x: x.count()),
        '空值计数': grouped_5.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_5.loc['试验组'], stats_df_5.loc['对照组']])
    # 在stats_df_5中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_5['检验方法'] = '卡方检验'
    stats_df_5['统计量'] = chi2_test_result[0]
    stats_df_5['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”5.浅表淋巴结“列中不同值的计数和占比
    value_counts = grouped_5.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_5.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_5_5
    stats_df_5_5 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_5)
    st.write(stats_df_5_5)

    # 根据df_1中label列的值不同，分组统计df_1中”6.胸部“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比  
    st.markdown('## 胸部')
    # 根据df_1中label列的值不同，分组统计df_1中”6.胸部“列中非空值的计数和空值计数
    grouped_6 = df_1.groupby('label')['6.胸部']
    stats_df_6 = pd.DataFrame({
        '非空值计数': grouped_6.apply(lambda x: x.count()),
        '空值计数': grouped_6.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_6.loc['试验组'], stats_df_6.loc['对照组']])
    # 在stats_df_6中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_6['检验方法'] = '卡方检验'
    stats_df_6['统计量'] = chi2_test_result[0]
    stats_df_6['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”6.胸部“列中不同值的计数和占比
    value_counts = grouped_6.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_6.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_6_6
    stats_df_6_6 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_6)
    st.write(stats_df_6_6)

    # 根据df_1中label列的值不同，分组统计df_1中”7.腹部“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 腹部')
    # 根据df_1中label列的值不同，分组统计df_1中”7.腹部“列中非空值的计数和空值计数
    grouped_7 = df_1.groupby('label')['7.腹部']
    stats_df_7 = pd.DataFrame({
        '非空值计数': grouped_7.apply(lambda x: x.count()),
        '空值计数': grouped_7.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_7.loc['试验组'], stats_df_7.loc['对照组']])
    # 在stats_df_7中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_7['检验方法'] = '卡方检验'
    stats_df_7['统计量'] = chi2_test_result[0]
    stats_df_7['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”7.腹部“列中不同值的计数和占比
    value_counts = grouped_7.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_7.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_7_7
    stats_df_7_7 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_7)
    st.write(stats_df_7_7)

    # 根据df_1中label列的值不同，分组统计df_1中”8.脊柱/四肢“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 脊柱/四肢')
    # 根据df_1中label列的值不同，分组统计df_1中”8.脊柱/四肢“列中非空值的计数和空值计数
    grouped_8 = df_1.groupby('label')['8.脊柱/四肢']
    stats_df_8 = pd.DataFrame({
        '非空值计数': grouped_8.apply(lambda x: x.count()),
        '空值计数': grouped_8.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_8.loc['试验组'], stats_df_8.loc['对照组']])
    # 在stats_df_8中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_8['检验方法'] = '卡方检验'
    stats_df_8['统计量'] = chi2_test_result[0]
    stats_df_8['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”8.脊柱/四肢“列中不同值的计数和占比
    value_counts = grouped_8.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_8.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_8_8
    stats_df_8_8 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_8)
    st.write(stats_df_8_8)

    # 根据df_1中label列的值不同，分组统计df_1中”9.神经系统“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 神经系统')
    # 根据df_1中label列的值不同，分组统计df_1中”9.神经系统“列中非空值的计数和空值计数
    grouped_9 = df_1.groupby('label')['9.神经系统']
    stats_df_9 = pd.DataFrame({
        '非空值计数': grouped_9.apply(lambda x: x.count()),
        '空值计数': grouped_9.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_9.loc['试验组'], stats_df_9.loc['对照组']])
    # 在stats_df_9中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_9['检验方法'] = '卡方检验'
    stats_df_9['统计量'] = chi2_test_result[0]
    stats_df_9['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”9.神经系统“列中不同值的计数和占比
    value_counts = grouped_9.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_9.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_9_9
    stats_df_9_9 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_9)
    st.write(stats_df_9_9)

    # 根据df_1中label列的值不同，分组统计df_1中”10、其他异常，请详述“列中不同值的非空值计数、空值计数、不同值的计数、不同值的百分比
    st.markdown('## 其他异常，请详述')
    # 根据df_1中label列的值不同，分组统计df_1中”10、其他异常，请详述“列中非空值的计数和空值计数
    grouped_10 = df_1.groupby('label')['10、其他异常，请详述']
    stats_df_10 = pd.DataFrame({
        '非空值计数': grouped_10.apply(lambda x: x.count()),
        '空值计数': grouped_10.apply(lambda x: x.isnull().sum())
    })
    # 为两组非空值计数的差异进行卡方检验
    chi2_test_result = stats.chi2_contingency([stats_df_10.loc['试验组'], stats_df_10.loc['对照组']])
    # 在stats_df_10中添加新的列”检验方法“，”统计量“和”p值“
    stats_df_10['检验方法'] = '卡方检验'
    stats_df_10['统计量'] = chi2_test_result[0]
    stats_df_10['p值'] = chi2_test_result[1]
    # 根据df_1中label列的值不同，分组统计df_1中”10、其他异常，请详述“列中不同值的计数和占比
    value_counts = grouped_10.value_counts().unstack().fillna(0)
    # 为两组不同值的计数进行卡方检验
    chi2_test_result = stats.chi2_contingency([value_counts.loc['试验组'], value_counts.loc['对照组']])
    # 为value_counts添加”检验方法“，”统计量“和”p值“三列
    value_counts['检验方法'] = '卡方检验'
    value_counts['统计量'] = chi2_test_result[0]
    value_counts['p值'] = chi2_test_result[1]
    value_counts_percent = grouped_10.value_counts(normalize=True).unstack().fillna(0) * 100
    # 给value_counts_percent的列名加上“占比(%)”
    value_counts_percent.columns = [str(col) + '_占比(%)' for col in value_counts_percent.columns]
    # 合并value_counts，value_counts_percent为stats_df_10_10
    stats_df_10_10 = pd.concat([value_counts, value_counts_percent], axis=1)
    st.write(stats_df_10)
    st.write(stats_df_10_10)
    





    # 遍历并获取tab16_dict中的key名包括字符串“#新冠核酸检测"的key对应的df，存入一个新的dict
    tab16_dict_4 = {}
    for key in tab16_dict.keys():
        if '#新冠核酸检测' in key:
            tab16_dict_4[key] = tab16_dict[key]
    # 遍历并计算tab16_dict_4中每个df的”是否进行新冠核酸检测？“列的非空值计数和空值计数（根据label列值的不同分组），并计算非空值计数的百分比，形成一个新df，然后计算两组非空值计数的差异的卡方检验，将检验方法、统计量和p值存入刚才的df中。最后将所有的df存入一个新的dict
    st.write('## 新冠核酸检测')
    stats_dict = {}
    for key, df in tab16_dict_4.items():
        grouped = df.groupby('label')['是否进行新冠核酸检测？']
        stats_df = pd.DataFrame({
            '非空值计数': grouped.apply(lambda x: x.count()),
            '空值计数': grouped.apply(lambda x: x.isnull().sum())
        })
        
        # 计算非空值计数和空值计数的差值
        stats_df['差值'] = stats_df['非空值计数'] - stats_df['空值计数']
        # 如果任意列中有0值或np.nan值则不比较
        stats_df = stats_df.replace(0, np.nan).dropna()
        # 对差值进行卡方检验
        chi2_test_result = stats.chisquare(stats_df['差值'])
        # 将结果作为新的列添加到stats_df中
        stats_df['检验方法'] = '卡方检验'
        stats_df['统计量'] = chi2_test_result[0]
        stats_df['p值'] = chi2_test_result[1]

        st.write(key)
        st.write(stats_df)

        # 遍历并计算tab16_dict_4中每个df的”检测结果“列不同值的计数（根据label列值的不同分组），将计算结果形成一个新的df，存入一个新的dict
    st.write('## 新冠核酸阴性阳性预测')
    result_dict = {}
    for key, df in tab16_dict_4.items():
        grouped = df.groupby('label')['检测结果']
        result_df = grouped.value_counts().unstack().fillna(0)
        result_dict[key] = result_df
        st.write(key)
        st.write(result_df)



    

    



    


    
    
