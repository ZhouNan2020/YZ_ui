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
file = st.sidebar.file_uploader("上传xlsx文件", type="xlsx")


#%%

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
    # 显示tab16_dict中的第一个key对应的dataframe
    st.subheader('6.2.人口学资料')
    # st.write('6.2.人口学资料')
    # 从tab16data中读取名为“访视1筛选-基线（0天）#96603#人口学资料”的sheet,保存为一个dataframe
    tab16_1 = tab16_dict['访视1筛选-基线（0天）#96603#人口学资料']
    # 将tab16_1中的“出生日期”列的值转换为datetime格式，只保留年
    tab16_1['出生日期'] = pd.to_datetime(tab16_1['出生日期']).dt.year
    # 使用2023减去tab16_1中的出生年份，得到年龄，在tab16_1中添加一列名为age，值为年龄
    tab16_1['age'] = 2023 - tab16_1['出生日期']
    # 按照label列值的不同，分别求出tab16_1中“age”列的非空值计数、空值计数，平均值，中位数，Q1，Q3，最小值，最大值，存入一个dataframe中，命名为data1
    data1 = pd.DataFrame()
    data1['非空值计数'] = tab16_1.groupby('label')['age'].apply(lambda x: x.count())
    data1['空值计数'] = tab16_1.groupby('label')['age'].apply(lambda x: x.isnull().sum())
    data1['平均值'] = tab16_1.groupby('label')['age'].apply(lambda x: x.mean())
    data1['标准差'] = tab16_1.groupby('label')['age'].apply(lambda x: x.std())
    data1['中位数'] = tab16_1.groupby('label')['age'].apply(lambda x: x.median())
    data1['Q1'] = tab16_1.groupby('label')['age'].apply(lambda x: x.quantile(0.25))
    data1['Q3'] = tab16_1.groupby('label')['age'].apply(lambda x: x.quantile(0.75))
    data1['最小值'] = tab16_1.groupby('label')['age'].apply(lambda x: x.min())
    data1['最大值'] = tab16_1.groupby('label')['age'].apply(lambda x: x.max())
    # 为data1添加试验组和对照组，作为index
    data1.index = ['试验组', '对照组']
    data1 = data1.T
    # data1添加“检验方法”，“统计量”，“p值”三列
    data1['检验方法'] = np.nan
    data1['统计量'] = np.nan
    data1['p值'] = np.nan
    # 并使用卡方检验计算卡方值和p值
    data1['检验方法']['非空值计数'] = '卡方检验'
    data1['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['age'].notnull()))[0]
    data1['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['age'].notnull()))[1]
    data1['检验方法']['非空值计数'] = '卡方检验'
    # 使用t检验计算平均值的t值和p值，检验方法为t检验
    data1['检验方法']['平均值'] = 't检验'
    data1['统计量']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['age'].dropna(),
                                             tab16_1[tab16_1['label'] == '对照组']['age'].dropna())[0]
    data1['p值']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['age'].dropna(),
                                             tab16_1[tab16_1['label'] == '对照组']['age'].dropna())[1]
    # 使用Wilcoxon秩和检验计算年龄列中不同值的U值和p值（不包括空值）
    data1['检验方法']['中位数'] = 'Wilcoxon秩和检验'
    data1['统计量']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['age'].dropna(),
                                                tab16_1[tab16_1['label'] == '对照组']['age'].dropna())[0]
    data1['p值']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['age'].dropna(),
                                                tab16_1[tab16_1['label'] == '对照组']['age'].dropna())[1]
    st.write('年龄')
    st.write(data1)
    # 按照label列值的不同，分别求出tab16_1中“性别”列的非空值计数与空值计数，并计算非空值计数占总数的比例，存入一个dataframe中，命名为data2
    data2 = pd.DataFrame()
    data2['非空值计数'] = tab16_1.groupby('label')['性别'].apply(lambda x: x.count())
    data2['空值计数'] = tab16_1.groupby('label')['性别'].apply(lambda x: x.isnull().sum())
    data2['男'] = tab16_1.groupby('label')['性别'].apply(lambda x: x[x == '男'].count())
    data2['女'] = tab16_1.groupby('label')['性别'].apply(lambda x: x[x == '女'].count())
    data2['男占比'] = (data2['男'] / data2['非空值计数'] * 100).apply(lambda x: '{0:.2f}%'.format(x))
    data2['女占比'] = (data2['女'] / data2['非空值计数'] * 100).apply(lambda x: '{0:.2f}%'.format(x))
    # 为data2添加试验组和对照组，作为index
    data2.index = ['试验组', '对照组']
    data2 = data2.T
    # data2添加“检验方法”，“统计量”，“p值”三列
    data2['检验方法'] = np.nan
    data2['统计量'] = np.nan
    data2['p值'] = np.nan
    # 使用卡方检验计算卡方值和p值
    data2['检验方法']['非空值计数'] = '卡方检验'
    data2['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['性别'].notnull()))[0]
    data2['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['性别'].notnull()))[1]
    # 使用卡方检验计算性别列中不同值的卡方值和p值（不包括空值）
    data2['检验方法']['男'] = '卡方检验'
    data2['统计量']['男'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['性别'] == '男'))[0]
    data2['p值']['男'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['性别'] == '男'))[1]
    st.write('性别')
    st.write(data2)
    # 按照label列值的不同，分别求出tab16_1中“民族”列
    # 将tab16_1的民族列中不为“汉”的值替换为“其他”（不包括空值，空值依旧保留）
    tab16_1['民族'] = tab16_1['民族'].apply(lambda x: '其他' if x != '汉' else x)
    data3 = pd.DataFrame()
    data3['非空值计数'] = tab16_1.groupby('label')['民族'].apply(lambda x: x.count())
    data3['空值计数'] = tab16_1.groupby('label')['民族'].apply(lambda x: x.isnull().sum())
    # 按照label列值的不同，分别求出tab16_1中“民族”列中值为“汉族”和不为“汉族”的计数
    data3['汉'] = tab16_1.groupby('label')['民族'].apply(lambda x: x[x == '汉'].count())
    data3['其他'] = tab16_1.groupby('label')['民族'].apply(lambda x: x[x != '汉'].count())
    # 按照label列值的不同，分别求出tab16_1中“民族”列中值为“汉族”和不为“汉族”的计数占总数的比例
    data3['汉族占比'] = (data3['汉'] / data3['非空值计数'] * 100).apply(lambda x: '{0:.2f}%'.format(x))
    data3['其他占比'] = (data3['其他'] / data3['非空值计数'] * 100).apply(lambda x: '{0:.2f}%'.format(x))
    # 为data3添加试验组和对照组，作为index
    data3.index = ['试验组', '对照组']
    data3 = data3.T
    # data3添加“检验方法”，“统计量”，“p值”三列
    data3['检验方法'] = np.nan
    data3['统计量'] = np.nan
    data3['p值'] = np.nan
    # 使用卡方检验计算卡方值和p值
    data3['检验方法']['非空值计数'] = '卡方检验'
    data3['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['民族'].notnull()))[0]
    data3['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['民族'].notnull()))[1]
    # 使用卡方检验计算民族列中值为“汉族”和值不为“汉族”的卡方值和p值（不包括空值）
    data3['检验方法']['汉'] = '卡方检验'
    data3['统计量']['汉'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['民族'] == '汉'))[0]
    data3['p值']['汉'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['民族'] == '汉'))[1]
    st.write('民族')
    st.write(data3)
    # 按照label列值的不同，分别求出tab16_1中“身高”列的非空值计数、空值计数，平均值，中位数，Q1，Q3，最小值，最大值，存入一个dataframe中，命名为data4
    data4 = pd.DataFrame()
    data4['非空值计数'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.count())
    data4['空值计数'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.isnull().sum())
    data4['平均值'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.mean())
    data4['标准差'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.std())
    data4['中位数'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.median())
    data4['Q1'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.quantile(0.25))
    data4['Q3'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.quantile(0.75))
    data4['最小值'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.min())
    data4['最大值'] = tab16_1.groupby('label')['身高'].apply(lambda x: x.max())
    # 为data4添加试验组和对照组，作为index
    data4.index = ['试验组', '对照组']
    data4 = data4.T
    # data4添加“检验方法”，“统计量”，“p值”三列
    data4['检验方法'] = np.nan
    data4['统计量'] = np.nan
    data4['p值'] = np.nan
    # 使用t检验计算身高列中不同值的t值和p值（不包括空值）
    data4['检验方法']['非空值计数'] = '卡方检验'
    data4['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['身高'].notnull()))[0]
    data4['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['身高'].notnull()))[1]
    # 使用t检验计算身高列中不同值的t值和p值（不包括空值）
    data4['检验方法']['平均值'] = 't检验'
    data4['统计量']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['身高'].dropna(), 
                                            tab16_1[tab16_1['label'] == '对照组']['身高'].dropna())[0]
    data4['p值']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['身高'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['身高'].dropna())[1]
    # 使用Wilcoxon秩和检验计算身高列中不同值的U值和p值（不包括空值）
    data4['检验方法']['中位数'] = 'Wilcoxon秩和检验'
    data4['统计量']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['身高'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['身高'].dropna())[0]
    data4['p值']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['身高'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['身高'].dropna())[1]
    st.write('身高')
    st.write(data4)
    # 按照label列值的不同，分别求出tab16_1中“体重”列的非空值计数、空值计数，平均值，中位数，Q1，Q3，最小值，最大值，存入一个dataframe中，命名为data5
    data5 = pd.DataFrame()
    data5['非空值计数'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.count())
    data5['空值计数'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.isnull().sum())
    data5['平均值'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.mean())
    data5['标准差'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.std())
    data5['中位数'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.median())
    data5['Q1'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.quantile(0.25))
    data5['Q3'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.quantile(0.75))
    data5['最小值'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.min())
    data5['最大值'] = tab16_1.groupby('label')['体重'].apply(lambda x: x.max())
    # 为data5添加试验组和对照组，作为index
    data5.index = ['试验组', '对照组']
    data5 = data5.T
    # data5添加“检验方法”，“统计量”，“p值”三列
    data5['检验方法'] = np.nan
    data5['统计量'] = np.nan
    data5['p值'] = np.nan
    # 使用t检验计算体重列中不同值的t值和p值（不包括空值）
    data5['检验方法']['非空值计数'] = '卡方检验'
    data5['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['体重'].notnull()))[0]
    data5['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['体重'].notnull()))[1]
    # 使用t检验计算体重列中不同值的t值和p值（不包括空值）
    data5['检验方法']['平均值'] = 't检验'
    data5['统计量']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['体重'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['体重'].dropna())[0]
    data5['p值']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['体重'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['体重'].dropna())[1]
    # 使用Wilcoxon秩和检验计算体重列中不同值的U值和p值（不包括空值）
    data5['检验方法']['中位数'] = 'Wilcoxon秩和检验'
    data5['统计量']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['体重'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['体重'].dropna())[0]
    data5['p值']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['体重'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['体重'].dropna())[1]
    st.write('体重')
    st.write(data5)
    # 按照label列值的不同，分别求出tab16_1中“BMI”列的非空值计数、空值计数，平均值，中位数，Q1，Q3，最小值，最大值，存入一个dataframe中，命名为data6
    data6 = pd.DataFrame()
    data6['非空值计数'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.count())
    data6['空值计数'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.isnull().sum())
    data6['平均值'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.mean())
    data6['标准差'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.std())
    data6['中位数'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.median())
    data6['Q1'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.quantile(0.25))
    data6['Q3'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.quantile(0.75))
    data6['最小值'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.min())
    data6['最大值'] = tab16_1.groupby('label')['BMI'].apply(lambda x: x.max())
    # 为data6添加试验组和对照组，作为index
    data6.index = ['试验组', '对照组']
    data6 = data6.T
    # data6添加“检验方法”，“统计量”，“p值”三列
    data6['检验方法'] = np.nan
    data6['统计量'] = np.nan
    data6['p值'] = np.nan
    # 使用t检验计算BMI列中不同值的t值和p值（不包括空值）
    data6['检验方法']['非空值计数'] = '卡方检验'
    data6['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['BMI'].notnull()))[0]
    data6['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_1['label'], tab16_1['BMI'].notnull()))[1]
    # 使用t检验计算BMI列中不同值的t值和p值（不包括空值）
    data6['检验方法']['平均值'] = 't检验'
    data6['统计量']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['BMI'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['BMI'].dropna())[0]
    data6['p值']['平均值'] = stats.ttest_ind(tab16_1[tab16_1['label'] == '试验组']['BMI'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['BMI'].dropna())[1]
    # 使用Wilcoxon秩和检验计算BMI列中不同值的U值和p值（不包括空值）
    data6['检验方法']['中位数'] = 'Wilcoxon秩和检验'
    data6['统计量']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['BMI'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['BMI'].dropna())[0]
    data6['p值']['中位数'] = stats.ranksums(tab16_1[tab16_1['label'] == '试验组']['BMI'].dropna(),
                                        tab16_1[tab16_1['label'] == '对照组']['BMI'].dropna())[1]
    st.write('BMI')
    st.write(data6)
    st.subheader('6.3.2饮酒史')
    # 提取出tab16_dict中名为“访视1筛选-基线（0天）#96605#饮酒史”的数据，存入tab16_2
    tab16_2 = tab16_dict['访视1筛选-基线（0天）#96605#饮酒史']
    # 根据label列值的不同，提取”是否有过饮酒史？”列中的非空值计数和空值计数，存入data7
    data7 = pd.DataFrame()
    data7['非空值计数'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x.count())
    data7['空值计数'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x.isnull().sum())
    # 根据label列值的不同，计算“是否有过饮酒史？”列中值为”否“和值不为”否“的个数和占比（跳过nan值），存入data7
    data7['否计数'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x[x == '否'].count())
    data7['否占比'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x[x == '否'].count() / x.count())
    data7['非否计数'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x[x != '否'].count())
    data7['非否占比'] = tab16_2.groupby('label')['是否有过饮酒史？'].apply(lambda x: x[x != '否'].count() / x.count())
    # 为data7添加试验组和对照组，作为index
    data7.index = ['试验组', '对照组']
    # 转置
    data7 = data7.T
    # data7添加“检验方法”，“统计量”，“p值”三列
    data7['检验方法'] = np.nan
    data7['统计量'] = np.nan
    data7['p值'] = np.nan
    # 使用卡方检验计算“是否有过饮酒史？”列中不同值的卡方值和p值（不包括空值）
    data7['检验方法']['非空值计数'] = '卡方检验'
    data7['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否有过饮酒史？'].notnull()))[0]
    data7['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否有过饮酒史？'].notnull()))[1]
    # 使用卡方检验计算“是否有过饮酒史？”列”否计数“和”非否计数“的卡方值和p值（不包括空值）
    data7['检验方法']['否计数'] = '卡方检验'
    data7['统计量']['否计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否有过饮酒史？'] == '否'))[0]
    data7['p值']['否计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否有过饮酒史？'] == '否'))[1]
    # 把data7索引中的“非否计数”和“非否占比”改为“是计数”和“是占比”
    data7.rename(index={'非否计数': '是计数', '非否占比': '是占比'}, inplace=True)
    st.write('是否有过饮酒史？')
    st.write(data7)
    # 根据label列值的不同，计算tab16_2中”是否戒酒？“列中非空值计数和空值计数，存入data8
    data8 = pd.DataFrame()
    data8['非空值计数'] = tab16_2.groupby('label')['是否戒酒？'].apply(lambda x: x.count())
    data8['空值计数'] = tab16_2.groupby('label')['是否戒酒？'].apply(lambda x: x.isnull().sum())
    data8.index = ['试验组', '对照组']
    # 卡方检验计算”是否戒酒？“列中不同组计数的卡方值和p值
    data8['检验方法'] = '卡方检验'
    data8['统计量'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否戒酒？'].notnull()))[0]
    data8['p值'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否戒酒？'].notnull()))[1]
    # 转置
    data8 = data8.T
    # 根据label列值的不同，计算”是否戒酒？“列中不同值的个数,存入data8_1
    data8_1 = pd.DataFrame()
    # 获取”是否戒酒？“列的描述性统计信息
    data8_1['试验组'] = tab16_2[tab16_2['label'] == '试验组']['是否戒酒？'].value_counts()
    data8_1['对照组'] = tab16_2[tab16_2['label'] == '对照组']['是否戒酒？'].value_counts()
    # data8_1增加占比计算
    data8_1['试验组占比'] = tab16_2[tab16_2['label'] == '试验组']['是否戒酒？'].value_counts() / tab16_2[tab16_2['label'] == '试验组']['是否戒酒？'].count()
    data8_1['对照组占比'] = tab16_2[tab16_2['label'] == '对照组']['是否戒酒？'].value_counts() / tab16_2[tab16_2['label'] == '对照组']['是否戒酒？'].count()
    st.write('是否戒酒？')
    st.write(data8)
    # data8_1添加“检验方法”，“统计量”，“p值”三列
    data8_1['检验方法'] = np.nan
    data8_1['统计量'] = np.nan
    data8_1['p值'] = np.nan
    # 按照data8_1中所体现的值不同，对两组进行卡方检验，分别计算出统计量和p值
    for index in data8_1.index:
        data8_1['检验方法'][index] = '卡方检验'
        data8_1['统计量'][index], data8_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['是否戒酒？'] == index))[:2]
    st.write(data8_1)
    # 根据label列值的不同，计算tab16_2中”请详述戒酒年限“列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data9 = pd.DataFrame()
    data9['非空值计数'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.count())
    data9['空值计数'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.isnull().sum())
    data9['平均值'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.mean())
    data9['标准差'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.std())
    data9['中位数'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.median())
    data9['Q1'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.quantile(0.25))
    data9['Q3'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.quantile(0.75))
    data9['最小值'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.min())
    data9['最大值'] = tab16_2.groupby('label')['请详述戒酒年限'].apply(lambda x: x.max())
    data9.index = ['试验组', '对照组']
    # 转置
    data9 = data9.T
    # data9添加“检验方法”，“统计量”，“p值”三列
    data9['检验方法'] = np.nan
    data9['统计量'] = np.nan
    data9['p值'] = np.nan
    # 使用卡方检验，计算出该列计数的统计量和p值
    data9['检验方法']['非空值计数'] = '卡方检验'
    data9['统计量']['非空值计数'], data9['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['请详述戒酒年限'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data9['检验方法']['平均值'] = 't检验'
    data9['统计量']['平均值'], data9['p值']['平均值'] = stats.ttest_ind(tab16_2[tab16_2['label'] == '试验组']['请详述戒酒年限'], tab16_2[tab16_2['label'] == '对照组']['请详述戒酒年限'], equal_var=False)[:2]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data9['检验方法']['中位数'] = 'wilcoxon检验'
    data9['统计量']['中位数'], data9['p值']['中位数'] = stats.wilcoxon(tab16_2[tab16_2['label'] == '试验组']['请详述戒酒年限'], tab16_2[tab16_2['label'] == '对照组']['请详述戒酒年限'])[:2]
    st.write('请详述戒酒年限')
    st.write(data9)
    # 根据label列值的不同，计算tab16_2中“饮酒年限”列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data10 = pd.DataFrame()
    data10['非空值计数'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.count())
    data10['空值计数'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.isnull().sum())
    data10['平均值'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.mean())
    data10['标准差'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.std())
    data10['中位数'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.median())
    data10['Q1'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.quantile(0.25))
    data10['Q3'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.quantile(0.75))
    data10['最小值'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.min())
    data10['最大值'] = tab16_2.groupby('label')['饮酒年限'].apply(lambda x: x.max())
    data10.index = ['试验组', '对照组']
    # 转置
    data10 = data10.T
    # data10添加“检验方法”，“统计量”，“p值”三列
    data10['检验方法'] = np.nan
    data10['统计量'] = np.nan
    data10['p值'] = np.nan
    # 使用卡方检验，计算出该列不同组的计数的统计量和p值
    data10['检验方法']['非空值计数'] = '卡方检验'
    data10['统计量']['非空值计数'], data10['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['饮酒年限'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data10['检验方法']['平均值'] = 't检验'
    data10['统计量']['平均值'] = stats.ttest_ind(tab16_2[tab16_2['label'] == '试验组']['饮酒年限'], tab16_2[tab16_2['label'] == '对照组']['饮酒年限'], equal_var=False)[0]
    data10['p值']['平均值'] = stats.ttest_ind(tab16_2[tab16_2['label'] == '试验组']['饮酒年限'], tab16_2[tab16_2['label'] == '对照组']['饮酒年限'], equal_var=False)[1]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data10['检验方法']['中位数'] = 'wilcoxon检验'
    data10['统计量']['中位数'], data10['p值']['中位数'] = stats.wilcoxon(tab16_2[tab16_2['label'] == '试验组']['饮酒年限'], tab16_2[tab16_2['label'] == '对照组']['饮酒年限'])[:2]
    st.write('饮酒年限')
    st.write(data10)
    # 将tab16_2中”请详述饮酒量“列中的”UK“替换为nan
    tab16_2['请详述饮酒量'] = tab16_2['请详述饮酒量'].replace('UK', np.nan)
    # 根据label列值的不同，计算tab16_2中”请详述饮酒量“列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data11 = pd.DataFrame()
    data11['非空值计数'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.count())
    data11['空值计数'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.isnull().sum())
    data11['平均值'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.mean())
    data11['标准差'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.std())
    data11['中位数'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.median())
    data11['Q1'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.quantile(0.25))
    data11['Q3'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.quantile(0.75))
    data11['最小值'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.min())
    data11['最大值'] = tab16_2.groupby('label')['请详述饮酒量'].apply(lambda x: x.max())
    data11.index = ['试验组', '对照组']
    # 转置
    data11 = data11.T
    # data11添加“检验方法”，“统计量”，“p值”三列
    data11['检验方法'] = np.nan
    data11['统计量'] = np.nan
    data11['p值'] = np.nan
    # 使用卡方检验，计算出该列不同组的计数的统计量和p值
    data11['检验方法']['非空值计数'] = '卡方检验'
    data11['统计量']['非空值计数'], data11['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_2['label'], tab16_2['请详述饮酒量'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data11['检验方法']['平均值'] = 't检验'
    data11['统计量']['平均值'], data11['p值']['平均值'] = stats.ttest_ind(tab16_2[tab16_2['label'] == '试验组']['请详述饮酒量'], tab16_2[tab16_2['label'] == '对照组']['请详述饮酒量'], equal_var=False)[:2]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data11['检验方法']['中位数'] = 'wilcoxon检验'
    data11['统计量']['中位数'], data11['p值']['中位数'] = stats.wilcoxon(tab16_2[tab16_2['label'] == '试验组']['请详述饮酒量'], tab16_2[tab16_2['label'] == '对照组']['请详述饮酒量'])[:2]
    st.write('请详述饮酒量')
    st.write(data11)
    st.subheader('表6.3.3吸烟史')
    # 从tab16_dict中提取'访视1筛选-基线（0天）#96626#吸烟史'
    tab16_3 = tab16_dict['访视1筛选-基线（0天）#96626#吸烟史']
    # 将tab16_3中”吸烟年限“列中的”UK“替换为nan
    tab16_3['吸烟年限'] = tab16_3['吸烟年限'].replace('UK', np.nan)
    # 根据label列值的不同，提取”是否有过饮酒史？”列中的非空值计数和空值计数，存入data12
    data12 = pd.DataFrame()
    data12['非空值计数'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x.count())
    data12['空值计数'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x.isnull().sum())
    # 根据label列值的不同，计算“是否有过饮酒史？”列中值为”否“和值不为”否“的个数和占比（跳过nan值），存入data12
    data12['否计数'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x[x == '否'].count())
    data12['否占比'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x[x == '否'].count() / x.count())
    data12['非否计数'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x[x != '否'].count())
    data12['非否占比'] = tab16_3.groupby('label')['是否有过吸烟史？'].apply(lambda x: x[x != '否'].count() / x.count())
    # 为data12添加试验组和对照组，作为index
    data12.index = ['试验组', '对照组']
    # 转置
    data12 = data12.T
    # data12添加“检验方法”，“统计量”，“p值”三列
    data12['检验方法'] = np.nan
    data12['统计量'] = np.nan
    data12['p值'] = np.nan
    # 使用卡方检验计算“是否有过饮酒史？”列中不同值的卡方值和p值（不包括空值）
    data12['检验方法']['非空值计数'] = '卡方检验'
    data12['统计量']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否有过吸烟史？'].notnull()))[0]
    data12['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否有过吸烟史？'].notnull()))[1]
    # 使用卡方检验计算“是否有过饮酒史？”列”否计数“和”非否计数“的卡方值和p值（不包括空值）
    data12['检验方法']['否计数'] = '卡方检验'
    data12['统计量']['否计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否有过吸烟史？']))[0]
    data12['p值']['否计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否有过吸烟史？']))[1]
    # 把data7索引中的“非否计数”和“非否占比”改为“是计数”和“是占比”
    data12.rename(index={'非否计数': '是计数', '非否占比': '是占比'}, inplace=True)
    st.write('是否有过吸烟史？')
    st.write(data12)
    # 根据label列值的不同，计算tab16_3中”是否戒酒？“列中非空值计数和空值计数，存入data13
    data13 = pd.DataFrame()
    data13['非空值计数'] = tab16_3.groupby('label')['是否戒烟？'].apply(lambda x: x.count())
    data13['空值计数'] = tab16_3.groupby('label')['是否戒烟？'].apply(lambda x: x.isnull().sum())
    data13.index = ['试验组', '对照组']
    # 卡方检验计算”是否戒酒？“列中不同组计数的卡方值和p值
    data13['检验方法'] = '卡方检验'
    data13['统计量'], data13['p值'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否戒烟？'].notnull()))[:2]
    # 转置
    data13 = data13.T
    # 根据label列值的不同，计算”是否戒酒？“列中不同值的个数,存入data13_1
    data13_1 = pd.DataFrame()
    # 获取”是否戒酒？“列的描述性统计信息
    data13_1['试验组'] = tab16_3[tab16_3['label'] == '试验组']['是否戒烟？'].value_counts()
    data13_1['对照组'] = tab16_3[tab16_3['label'] == '对照组']['是否戒烟？'].value_counts()
    # data13_1增加占比计算
    data13_1['试验组占比'] = tab16_3[tab16_3['label'] == '试验组']['是否戒烟？'].value_counts() / tab16_3[tab16_3['label'] == '试验组']['是否戒烟？'].count()
    data13_1['对照组占比'] = tab16_3[tab16_3['label'] == '对照组']['是否戒烟？'].value_counts() / tab16_3[tab16_3['label'] == '对照组']['是否戒烟？'].count()
    st.write('是否戒烟？')
    st.write(data13)
    # data13_1添加“检验方法”，“统计量”，“p值”三列
    data13_1['检验方法'] = np.nan
    data13_1['统计量'] = np.nan
    data13_1['p值'] = np.nan
    # 按照data13_1中所体现的值不同，对两组进行卡方检验，分别计算出统计量和p值
    for index in data13_1.index:
        data13_1['检验方法'][index] = '卡方检验'
        data13_1['统计量'][index], data13_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['是否戒烟？'] == index))[:2]
    st.write(data13_1)
    # 根据label列值的不同，计算tab16_3中”请详述戒烟年限“列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data14 = pd.DataFrame()
    data14['非空值计数'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.count())
    data14['空值计数'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.isnull().sum())
    data14['平均值'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.mean())
    data14['标准差'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.std())
    data14['中位数'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.median())
    data14['Q1'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.quantile(0.25))
    data14['Q3'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.quantile(0.75))
    data14['最小值'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.min())
    data14['最大值'] = tab16_3.groupby('label')['请详述戒烟年限'].apply(lambda x: x.max())
    data14.index = ['试验组', '对照组']
    # 转置
    data14 = data14.T
    # data14添加“检验方法”，“统计量”，“p值”三列
    data14['检验方法'] = np.nan
    data14['统计量'] = np.nan
    data14['p值'] = np.nan
    # 使用卡方检验，计算出该列计数的统计量和p值
    data14['检验方法']['非空值计数'] = '卡方检验'
    data14['统计量']['非空值计数'], data14['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['请详述戒烟年限'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data14['检验方法']['平均值'] = 't检验'
    data14['统计量']['平均值'], data14['p值']['平均值'] = stats.ttest_ind(tab16_3[tab16_3['label'] == '试验组']['请详述戒烟年限'], tab16_3[tab16_3['label'] == '对照组']['请详述戒烟年限'], equal_var=False)[:2]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data14['检验方法']['中位数'] = 'wilcoxon检验'
    data14['统计量']['中位数'], data14['p值']['中位数'] = stats.wilcoxon(tab16_3[tab16_3['label'] == '试验组']['请详述戒烟年限'], tab16_3[tab16_3['label'] == '对照组']['请详述戒烟年限'])[:2]
    st.write('请详述戒烟年限')
    st.write(data14)
    # 根据label列值的不同，计算tab16_3中“吸烟年限”列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data14 = pd.DataFrame()
    data14['非空值计数'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.count())
    data14['空值计数'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.isnull().sum())
    data14['平均值'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.mean())
    data14['标准差'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.std())
    data14['中位数'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.median())
    data14['Q1'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.quantile(0.25))
    data14['Q3'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.quantile(0.75))
    data14['最小值'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.min())
    data14['最大值'] = tab16_3.groupby('label')['吸烟年限'].apply(lambda x: x.max())
    data14.index = ['试验组', '对照组']
    # 转置
    data14 = data14.T
    # data14添加“检验方法”，“统计量”，“p值”三列
    data14['检验方法'] = np.nan
    data14['统计量'] = np.nan
    data14['p值'] = np.nan
    # 使用卡方检验，计算出该列不同组的计数的统计量和p值
    data14['检验方法']['非空值计数'] = '卡方检验'
    data14['统计量']['非空值计数'], data14['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['吸烟年限'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data14['检验方法']['平均值'] = 't检验'
    data14['统计量']['平均值'], data14['p值']['平均值'] = stats.ttest_ind(tab16_3[tab16_3['label'] == '试验组']['吸烟年限'], tab16_3[tab16_3['label'] == '对照组']['吸烟年限'], equal_var=False)[:2]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data14['检验方法']['中位数'] = 'wilcoxon检验'
    data14['统计量']['中位数'], data14['p值']['中位数'] = stats.wilcoxon(tab16_3[tab16_3['label'] == '试验组']['吸烟年限'], tab16_3[tab16_3['label'] == '对照组']['吸烟年限'])[:2]
    st.write('吸烟年限')
    st.write(data14)
    # 将tab16_3中”请详述吸烟量“列中的”UK“替换为nan
    tab16_3['请详述吸烟量'] = tab16_3['请详述吸烟量'].replace('UK', np.nan)
    # 根据label列值的不同，计算tab16_3中”请详述吸烟量“列中非空值计数、空值计数，平均值，标准差，中位数，Q1，Q3，最小值，最大值
    data15 = pd.DataFrame()
    data15['非空值计数'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.count())
    data15['空值计数'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.isnull().sum())
    data15['平均值'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.mean())
    data15['标准差'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.std())
    data15['中位数'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.median())
    data15['Q1'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.quantile(0.25))
    data15['Q3'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.quantile(0.75))
    data15['最小值'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.min())
    data15['最大值'] = tab16_3.groupby('label')['请详述吸烟量'].apply(lambda x: x.max())
    data15.index = ['试验组', '对照组']
    # 转置
    data15 = data15.T
    # data15添加“检验方法”，“统计量”，“p值”三列
    data15['检验方法'] = np.nan
    data15['统计量'] = np.nan
    data15['p值'] = np.nan
    # 使用卡方检验，计算出该列不同组的计数的统计量和p值
    data15['检验方法']['非空值计数'] = '卡方检验'
    data15['统计量']['非空值计数'], data15['p值']['非空值计数'] = stats.chi2_contingency(pd.crosstab(tab16_3['label'], tab16_3['请详述吸烟量'].notnull()))[:2]
    # 使用t检验，计算出该列不同组的统计量和p值
    data15['检验方法']['平均值'] = 't检验'
    data15['统计量']['平均值'], data15['p值']['平均值'] = stats.ttest_ind(tab16_3[tab16_3['label'] == '试验组']['请详述吸烟量'], tab16_3[tab16_3['label'] == '对照组']['请详述吸烟量'], equal_var=False)[:2]
    # 使用wilcoxon检验，计算出该列不同组的统计量和p值
    data15['检验方法']['中位数'] = 'wilcoxon检验'
    data15['统计量']['中位数'], data15['p值']['中位数'] = stats.wilcoxon(tab16_3[tab16_3['label'] == '试验组']['请详述吸烟量'], tab16_3[tab16_3['label'] == '对照组']['请详述吸烟量'])[:2]
    st.write('请详述吸烟量')
    st.write(data15)
    st.subheader('表6.3.4是否有过敏史？')
    # 从tab16_dict中提取“访视1筛选-基线（0天）#96627#过敏史“key对应的value
    tab16_4 = tab16_dict['访视1筛选-基线（0天）#96627#过敏史']
    # 获取tab16_4中“是否有过敏史？”列中的非空值计数，空值计数
    data16 = pd.DataFrame()
    data16['非空值计数'] = tab16_4.groupby('label')['是否有过敏史？'].apply(lambda x: x.count())
    data16['空值计数'] = tab16_4.groupby('label')['是否有过敏史？'].apply(lambda x: x.isnull().sum())
    data16.index = ['试验组', '对照组']
    # 添加“检验方法”，“统计量”，“p值”三列
    data16['检验方法'] = np.nan
    data16['统计量'] = np.nan
    data16['p值'] = np.nan
    # 卡方检验，计算出该列不同组的计数的统计量和p值
    data16['检验方法'] = '卡方检验'
    data16['统计量'], data16['p值'] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['是否有过敏史？'].notnull()))[:2]
    # 转置
    data16 = data16.T
    # 获取tab16_4中“是否有过敏史？”列中的不同值的计数和占比，占比使用百分数形式表示
    data16_1 = pd.DataFrame()
    data16_1['计数'] = tab16_4.groupby('label')['是否有过敏史？'].apply(lambda x: x.value_counts())
    data16_1['占比'] = tab16_4.groupby('label')['是否有过敏史？'].apply(lambda x: x.value_counts(normalize=True)).apply(lambda x: x * 100)
    # 添加“检验方法”，“统计量”，“p值”三列
    data16_1['检验方法'] = np.nan
    data16_1['统计量'] = np.nan
    data16_1['p值'] = np.nan
    # 卡方检验，计算出该列不同组的计数的统计量和p值
    data16_1['检验方法'] = '卡方检验'
    data16_1['统计量'], data16_1['p值'] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['是否有过敏史？']))[:2]
    # 转置
    st.write('是否有过敏史？')
    st.write(data16)
    st.write(data16_1)
    # 获取tab16_4中“药物过敏？”列中的非空值计数，空值计数
    data17 = pd.DataFrame()
    data17['非空值计数'] = tab16_4.groupby('label')['药物过敏？'].apply(lambda x: x.count())
    data17['空值计数'] = tab16_4.groupby('label')['药物过敏？'].apply(lambda x: x.isnull().sum())
    data17.index = ['试验组', '对照组']
    # 添加“检验方法”，“统计量”，“p值”三列
    data17['检验方法'] = np.nan
    data17['统计量'] = np.nan
    data17['p值'] = np.nan
    # 卡方检验，计算出该列不同组的非空值计数与空值计数的统计量和p值
    data17['检验方法'] = '卡方检验'
    data17['统计量'], data17['p值'] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['药物过敏？'].notnull()))[:2]
    # 转置
    data17 = data17.T
    # 获取tab16_4中“药物过敏？”列中的不同值的计数和占比，占比使用百分数形式表示
    data17_1 = pd.DataFrame()
    data17_1['计数'] = tab16_4.groupby('label')['药物过敏？'].apply(lambda x: x.value_counts())
    data17_1['占比'] = tab16_4.groupby('label')['药物过敏？'].apply(lambda x: x.value_counts(normalize=True)).apply(lambda x: x * 100)
    # 添加“检验方法”，“统计量”，“p值”三列
    data17_1['检验方法'] = np.nan
    data17_1['统计量'] = np.nan
    data17_1['p值'] = np.nan
    # 卡方检验，如果该列值为空，则统计量和p值为nan，如果该列值不为空，计算出该列不同组的值计数的统计量和p值
    for index in data17_1.index:
        if pd.isnull(data17_1['计数'][index]):
            data17_1['检验方法'][index] = np.nan
            data17_1['统计量'][index] = np.nan
            data17_1['p值'][index] = np.nan
        else:
            data17_1['检验方法'][index] = '卡方检验'
            data17_1['统计量'][index], data17_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['药物过敏？'] == index))[:2]
    # 转置
    st.write('药物过敏？')
    st.write(data17)
    st.write(data17_1)
    # 获取tab16_4中“食物过敏？”列中的非空值计数，空值计数
    data18 = pd.DataFrame()
    data18['非空值计数'] = tab16_4.groupby('label')['食物过敏？'].apply(lambda x: x.count())
    data18['空值计数'] = tab16_4.groupby('label')['食物过敏？'].apply(lambda x: x.isnull().sum())
    data18.index = ['试验组', '对照组']
    # 添加“检验方法”，“统计量”，“p值”三列
    data18['检验方法'] = np.nan
    data18['统计量'] = np.nan
    data18['p值'] = np.nan
    # 卡方检验，计算出该列不同组的非空值计数与空值计数的统计量和p值
    data18['检验方法'] = '卡方检验'
    data18['统计量'], data18['p值'] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['食物过敏？'].notnull()))[:2]
    # 转置
    data18 = data18.T
    # 获取tab16_4中“食物过敏？”列中的不同值的计数和占比，占比使用百分数形式表示
    data18_1 = pd.DataFrame()
    data18_1['计数'] = tab16_4.groupby('label')['食物过敏？'].apply(lambda x: x.value_counts())
    data18_1['占比'] = tab16_4.groupby('label')['食物过敏？'].apply(lambda x: x.value_counts(normalize=True)).apply(lambda x: x * 100)
    # 添加“检验方法”，“统计量”，“p值”三列
    data18_1['检验方法'] = np.nan
    data18_1['统计量'] = np.nan
    data18_1['p值'] = np.nan
    # 卡方检验，如果该列值为空，则统计量和p值为nan，如果该列值不为空，计算出该列不同组的值计数的统计量和p值
    for index in data18_1.index:
        if pd.isnull(data18_1['计数'][index]):
            data18_1['检验方法'][index] = np.nan
            data18_1['统计量'][index] = np.nan
            data18_1['p值'][index] = np.nan
        else:
            data18_1['检验方法'][index] = '卡方检验'
            data18_1['统计量'][index], data18_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['食物过敏？'] == index))[:2]
    # 转置
    st.write('食物过敏？')
    st.write(data18)
    st.write(data18_1)
    # 获取tab16_4中”其他过敏史？“列中的非空值计数，空值计数
    data19 = pd.DataFrame()
    data19['非空值计数'] = tab16_4.groupby('label')['其他过敏史？'].apply(lambda x: x.count())
    data19['空值计数'] = tab16_4.groupby('label')['其他过敏史？'].apply(lambda x: x.isnull().sum())
    data19.index = ['试验组', '对照组']
    # 添加“检验方法”，“统计量”，“p值”三列
    data19['检验方法'] = np.nan
    data19['统计量'] = np.nan  
    data19['p值'] = np.nan
    # 卡方检验，计算出该列不同组的非空值计数与空值计数的统计量和p值
    data19['检验方法'] = '卡方检验'
    data19['统计量'], data19['p值'] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['其他过敏史？'].notnull()))[:2]
    # 转置
    data19 = data19.T
    # 获取tab16_4中”其他过敏史？“列中的不同值的计数和占比，占比使用百分数形式表示
    data19_1 = pd.DataFrame()
    data19_1['计数'] = tab16_4.groupby('label')['其他过敏史？'].apply(lambda x: x.value_counts())
    data19_1['占比'] = tab16_4.groupby('label')['其他过敏史？'].apply(lambda x: x.value_counts(normalize=True)).apply(lambda x: x * 100)
    # 添加“检验方法”，“统计量”，“p值”三列
    data19_1['检验方法'] = np.nan
    data19_1['统计量'] = np.nan
    data19_1['p值'] = np.nan
    # 卡方检验，如果该列值为空，则统计量和p值为nan，如果该列值不为空，计算出该列不同组的值计数的统计量和p值
    for index in data19_1.index:
        if pd.isnull(data19_1['计数'][index]):
            data19_1['检验方法'][index] = np.nan
            data19_1['统计量'][index] = np.nan
            data19_1['p值'][index] = np.nan
        else:
            data19_1['检验方法'][index] = '卡方检验'
            data19_1['统计量'][index], data19_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_4['label'], tab16_4['其他过敏史？'] == index))[:2]
    # 转置
    st.write('其他过敏史？')
    st.write(data19)
    st.write(data19_1)
    # 获取tab16_dict中“访视1筛选-基线（0天）#96608#药物滥用史”key对应的value
    tab16_5 = tab16_dict['访视1筛选-基线（0天）#96608#药物滥用史']
    # 获取tab16_5中”是否有过药物滥用史？“列中的非空值计数，空值计数
    data20 = pd.DataFrame()
    data20['非空值计数'] = tab16_5.groupby('label')['是否有过药物滥用史？'].apply(lambda x: x.count())
    data20['空值计数'] = tab16_5.groupby('label')['是否有过药物滥用史？'].apply(lambda x: x.isnull().sum())
    data20.index = ['试验组', '对照组']
    # 添加“检验方法”，“统计量”，“p值”三列
    data20['检验方法'] = np.nan
    data20['统计量'] = np.nan
    data20['p值'] = np.nan
    # 卡方检验，计算出该列不同组的非空值计数与空值计数的统计量和p值
    data20['检验方法'] = '卡方检验'
    data20['统计量'], data20['p值'] = stats.chi2_contingency(pd.crosstab(tab16_5['label'], tab16_5['是否有过药物滥用史？'].notnull()))[:2]
    # 获取tab16_5中”是否有过药物滥用史？“列中的不同值的计数和占比，占比使用百分数形式表示
    data20_1 = pd.DataFrame()
    data20_1['计数'] = tab16_5.groupby('label')['是否有过药物滥用史？'].apply(lambda x: x.value_counts())
    data20_1['占比'] = tab16_5.groupby('label')['是否有过药物滥用史？'].apply(lambda x: x.value_counts(normalize=True)).apply(lambda x: x * 100)
    # 添加“检验方法”，“统计量”，“p值”三列
    data20_1['检验方法'] = np.nan
    data20_1['统计量'] = np.nan
    data20_1['p值'] = np.nan
    # 卡方检验，如果该列值为空，则统计量和p值为nan，如果该列值不为空，计算出该列不同组的值计数的统计量和p值
    for index in data20_1.index:
        if pd.isnull(data20_1['计数'][index]):
            data20_1['检验方法'][index] = np.nan
            data20_1['统计量'][index] = np.nan
            data20_1['p值'][index] = np.nan
        else:
            data20_1['检验方法'][index] = '卡方检验'
            data20_1['统计量'][index], data20_1['p值'][index] = stats.chi2_contingency(pd.crosstab(tab16_5['label'], tab16_5['是否有过药物滥用史？'] == index))[:2]
    # 转置
    st.write('是否有过药物滥用史？')
    st.write(data20)
    st.write(data20_1)


    with pd.ExcelWriter('匹配后全数据集.xlsx') as writer:  
        for key in tab16_dict.keys():
            tab16_dict[key].to_excel(writer, sheet_name=key)
    st.download_button(
        label="Download data as Excel",
        data=pd.read_excel('匹配后全数据集.xlsx').to_csv().encode('utf-8'),
        file_name="匹配后全数据集.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    
    
