import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
#%%

file = st.sidebar.file_uploader("上传xlsx文件", type="xlsx")

data = pd.ExcelFile(file)
data_dict = {}
for sheet in data.sheet_names:
    data_dict[sheet] = data.parse(sheet)
















#%%
dataInformedConsent = pd.concat([v for k,v in datadict.items() if '知情同意' in k], axis=0)
# 读取datadict中key名称中包括“生命体征”字符串的表格，形成一个dict
dataVitalSigns = {k:v for k,v in datadict.items() if '生命体征' in k}
# 读取dataVitalSigns中key的名称中包括“访视1”字符串的表格，形成一个df
dataVitalSigns1 = pd.concat([v for k,v in dataVitalSigns.items() if '访视1' in k], axis=0)
# 读取dataVitalSigns中key的名称中包括“访视4”字符串的表格，形成一个df
dataVitalSigns4 = pd.concat([v for k,v in dataVitalSigns.items() if '访视4' in k], axis=0)
# 将dataInformedConsent,dataVitalSigns1与dataVitalSigns4横向合并，以subject_id为索引
dataInformedConsentVitalSigns = dataInformedConsent.merge(dataVitalSigns1, on='subject_id').merge(dataVitalSigns4, on='subject_id')
# 在dataInformedConsentVitalSigns中提取所有列名中包含字符串'时间'和'日期'的列以及subject_id列，形成一个新的df
dataInformedConsentVitalSigns_time = dataInformedConsentVitalSigns[[col for col in dataInformedConsentVitalSigns.columns if '时间' in col or '日期' in col or 'subject_id' in col]]
# 将dataInformedConsentVitalSigns_time中的列除了”subject_id"列全部转换成datetime格式
dataInformedConsentVitalSigns_time = dataInformedConsentVitalSigns_time.apply(pd.to_datetime, errors='ignore')
# 使用”检查日期_x“列的值减去”本次访视时间“列的值，单位为天。得到一个新的列，列名为”基线生命体征检查时间与基线访视时间的差值“
dataInformedConsentVitalSigns_time['基线生命体征检查时间与基线访视时间的差值'] = dataInformedConsentVitalSigns_time['检查日期_x'] - dataInformedConsentVitalSigns_time['本次访视时间']
# 使用”检查日期_y“列的值减去”本次访视时间“列的值，单位为天。得到一个新的列，列名为”访视4（第7天）生命体征检查时间与基线访视时间的差值“
dataInformedConsentVitalSigns_time['访视4（第7天）生命体征检查时间与基线访视时间的差值'] = dataInformedConsentVitalSigns_time['检查日期_y'] - dataInformedConsentVitalSigns_time['本次访视时间']
datatimecheck1 = dataInformedConsentVitalSigns_time[['subject_id','基线生命体征检查时间与基线访视时间的差值','访视4（第7天）生命体征检查时间与基线访视时间的差值']]
# 在”基线生命体征检查时间与基线访视时间的差值“列后添加一个”是否异常“列，如果”基线生命体征检查时间与基线访视时间的差值“列的值不为0，则为异常，否则为空值
datatimecheck1['是否异常1'] = datatimecheck1['基线生命体征检查时间与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(0) else '')
# 在”访视4（第7天）生命体征检查时间与基线访视时间的差值“列后添加一个”是否异常“列，如果”访视4（第7天）生命体征检查时间与基线访视时间的差值“列的值不为7，则为异常，否则为空值
datatimecheck1['是否异常2'] = datatimecheck1['访视4（第7天）生命体征检查时间与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(7, unit='d') else '')
# 把“是否异常1”列挪到”访视4（第7天）生命体征检查时间与基线访视时间的差值“列前面，”基线生命体征检查时间与基线访视时间的差值“列后面
datatimecheck1 = datatimecheck1[['subject_id','是否异常1','基线生命体征检查时间与基线访视时间的差值','是否异常2','访视4（第7天）生命体征检查时间与基线访视时间的差值']]
#%%
# 保存datatimecheck1为excel

#%%
# Extract tables from datadict where the key name includes the string "体格检查" to form a df
dataPhysicalExamination = pd.concat([v for k,v in datadict.items() if '体格检查' in k], axis=0)
# Merge dataInformedConsent and dataPhysicalExamination horizontally, on='subject_id'
dataInformedConsentPhysicalExamination = dataInformedConsent.merge(dataPhysicalExamination, on='subject_id')

# Retain columns in dataInformedConsentPhysicalExamination that contain 'subject_id' and either '时间' or '日期' in their names
dataInformedConsentPhysicalExamination_time = dataInformedConsentPhysicalExamination.filter(regex='时间|日期|subject_id')

# Convert all columns except the first one in dataInformedConsentPhysicalExamination_time to datetime format
for column in dataInformedConsentPhysicalExamination_time.columns[1:]:
    dataInformedConsentPhysicalExamination_time[column] = pd.to_datetime(dataInformedConsentPhysicalExamination_time[column])

# Subtract the '本次访视时间' column from the '检查日期' column (in days) to create a new column named '基线体格检查时间与基线访视时间的差值'
dataInformedConsentPhysicalExamination_time['基线体格检查时间与基线访视时间的差值'] = (dataInformedConsentPhysicalExamination_time['检查日期'] - dataInformedConsentPhysicalExamination_time['本次访视时间']).dt.days
datatimecheck2 = dataInformedConsentPhysicalExamination_time[['subject_id','基线体格检查时间与基线访视时间的差值']]
# 如果”基线体格检查时间与基线访视时间的差值“列的值不为0，则为异常，否则为空值
datatimecheck2['是否异常'] = datatimecheck2['基线体格检查时间与基线访视时间的差值'].apply(lambda x: '异常' if x != 0 else '')
#%%
# 保存datatimecheck2为excel

#%%
# 提取datadict中key名称中包括“血常规”字符串但是不包括“其他异常结果”的字符串的表格，形成一个dict
dataBloodRoutine = {k:v for k,v in datadict.items() if '血常规' in k and '其他异常结果' not in k}
# 把dataInformedConsent分别merge到dataBloodRoutine中的每一个df中，on='subject_id'
dataBloodRoutine = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataBloodRoutine.items()}
# 所有的表格都只保存”subject_id","血常规是否有检查结果？”，“检查日期”和“本次访视时间”三列
dataBloodRoutine = {k:v.filter(items=['subject_id','血常规是否有检查结果？','检查日期','本次访视时间']) for k,v in dataBloodRoutine.items()}
# 遍历所有表格，如果“血常规是否有检查结果？”列中的值为“否”，则删除该行
dataBloodRoutine = {k:v[v['血常规是否有检查结果？'] == '是'] for k,v in dataBloodRoutine.items()}
# 将dataBloodRoutine中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataBloodRoutine = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataBloodRoutine.items()}
# 在dataBloodRoutine中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中血常规检查时间与基线访视时间的差值”
dataBloodRoutine = {k:v.assign(**{'本访视中血常规检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataBloodRoutine.items()}
# 给dataBloodRoutine中每一个df添加一个新的列，列名为“访视”，值为k
dataBloodRoutine = {k:v.assign(**{'访视':k}) for k,v in dataBloodRoutine.items()}
# 将“访视”列位置调整到第二列
dataBloodRoutine = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中血常规检查时间与基线访视时间的差值']) for k,v in dataBloodRoutine.items()}
# 纵向合并dataBloodRoutine中的所有df，形成一个大的df，以subject_id为索引
dataBloodRoutine = pd.concat(dataBloodRoutine.values(), axis=0)
# 设置subject_id为索引
dataBloodRoutine = dataBloodRoutine.set_index('subject_id')
# 保留访视，本次访视时间，本访视中血常规检查时间与基线访视时间的差值三列
dataBloodRoutine = dataBloodRoutine.filter(items=['访视', '本次访视时间', '本访视中血常规检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataBloodRoutine.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']
datatimecheck3 = dataBloodRoutine
#%%
# 提取datadict中key名称中包括“血生化”字符串但是不包括“其他异常结果”的字符串的表格，形成一个dict
dataBloodBiochemistry = {k:v for k,v in datadict.items() if '血生化' in k and '其他异常结果' not in k}
# 把dataInformedConsent分别merge到dataBloodBiochemistry中的每一个df中，on='subject_id'
dataBloodBiochemistry = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataBloodBiochemistry.items()}
# 所有的表格都只保存”subject_id","血生化是否有检查结果？",“检查日期”和“本次访视时间”三列
dataBloodBiochemistry = {k:v.filter(items=['subject_id','血生化是否有检查结果？','检查日期','本次访视时间']) for k,v in dataBloodBiochemistry.items()}
# 遍历所有表格，如果“血生化是否有检查结果？”列中的值为“否”，则删除该行
dataBloodBiochemistry = {k:v[v['血生化是否有检查结果？'] == '是'] for k,v in dataBloodBiochemistry.items()}
# 将dataBloodBiochemistry中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataBloodBiochemistry = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataBloodBiochemistry.items()}
# 在dataBloodBiochemistry中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中血生化检查时间与基线访视时间的差值”
dataBloodBiochemistry = {k:v.assign(**{'本访视中血生化检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataBloodBiochemistry.items()}
# 给dataBloodBiochemistry中每一个df添加一个新的列，列名为“访视”，值为k
dataBloodBiochemistry = {k:v.assign(**{'访视':k}) for k,v in dataBloodBiochemistry.items()}
# 将“访视”列位置调整到第二列
dataBloodBiochemistry = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中血生化检查时间与基线访视时间的差值']) for k,v in dataBloodBiochemistry.items()}
# 纵向合并dataBloodBiochemistry中的所有df，形成一个大的df，以subject_id为索引
dataBloodBiochemistry = pd.concat(dataBloodBiochemistry.values(), axis=0)
# 设置subject_id为索引
dataBloodBiochemistry = dataBloodBiochemistry.set_index('subject_id')
# 保留访视，本次访视时间，本访视中血生化检查时间与基线访视时间的差值三列
dataBloodBiochemistry = dataBloodBiochemistry.filter(items=['访视', '本次访视时间', '本访视中血生化检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataBloodBiochemistry.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck4 = dataBloodBiochemistry
#%%
# 提取datadict中key名称中包括“尿常规”字符串但是不包括“其他异常结果”的字符串的表格，形成一个dict
dataUrineRoutine = {k:v for k,v in datadict.items() if '尿常规' in k and '其他异常结果' not in k}
# 把dataInformedConsent分别merge到dataUrineRoutine中的每一个df中，on='subject_id'
dataUrineRoutine = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataUrineRoutine.items()}
# 所有的表格都只保存”subject_id","尿常规是否有检查结果？",“检查日期”和“本次访视时间”
dataUrineRoutine = {k:v.filter(items=['subject_id','尿常规是否有检查结果？','检查日期','本次访视时间']) for k,v in dataUrineRoutine.items()}
# 遍历所有表格，如果“尿常规是否有检查结果？”列中的值为“否”，则删除该行
dataUrineRoutine = {k:v[v['尿常规是否有检查结果？'] == '是'] for k,v in dataUrineRoutine.items()}
# 将dataUrineRoutine中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataUrineRoutine = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataUrineRoutine.items()}
# 在dataUrineRoutine中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中尿常规检查时间与基线访视时间的差值”
dataUrineRoutine = {k:v.assign(**{'本访视中尿常规检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataUrineRoutine.items()}
# 给dataUrineRoutine中每一个df添加一个新的列，列名为“访视”，值为k
dataUrineRoutine = {k:v.assign(**{'访视':k}) for k,v in dataUrineRoutine.items()}
# 将“访视”列位置调整到第二列
dataUrineRoutine = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中尿常规检查时间与基线访视时间的差值']) for k,v in dataUrineRoutine.items()}
# 纵向合并dataUrineRoutine中的所有df，形成一个大的df，以subject_id为索引
dataUrineRoutine = pd.concat(dataUrineRoutine.values(), axis=0)
# 设置subject_id为索引
dataUrineRoutine = dataUrineRoutine.set_index('subject_id')
# 保留访视，本次访视时间，本访视中尿常规检查时间与基线访视时间的差值三列
dataUrineRoutine = dataUrineRoutine.filter(items=['访视', '本次访视时间', '本访视中尿常规检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataUrineRoutine.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']
datatimecheck5 = dataUrineRoutine

#%%
# 提取datadict中key名称中包括“心电图”字符串的表格，形成一个dict
dataECG = {k:v for k,v in datadict.items() if '心电图' in k}
# 把dataInformedConsent分别merge到dataECG中的每一个df中，on='subject_id'
dataECG = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataECG.items()}
# 所有的表格都只保存”subject_id","心电图是否有检查结果？",“检查日期”和“本次访视时间”三列
dataECG = {k:v.filter(items=['subject_id', '心电图是否有检查结果？', '检查日期', '本次访视时间']) for k,v in dataECG.items()}
# 将dataECG中的所有df中“心电图是否有检查结果？”列的值为“是”的行保留，其余行删除
dataECG = {k:v[v['心电图是否有检查结果？'] == '是'] for k,v in dataECG.items()}
# 将dataECG中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataECG = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataECG.items()}
# 在dataECG中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中心电图检查时间与基线访视时间的差值”
dataECG = {k:v.assign(**{'本访视中心电图检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataECG.items()}
# 给dataECG中每一个df添加一个新的列，列名为“访视”，值为k
dataECG = {k:v.assign(**{'访视':k}) for k,v in dataECG.items()}
# 将“访视”列位置调整到第二列
dataECG = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中心电图检查时间与基线访视时间的差值']) for k,v in dataECG.items()}
# 纵向合并dataECG中的所有df，形成一个大的df，以subject_id为索引
dataECG = pd.concat(dataECG.values(), axis=0)
# 设置subject_id为索引
dataECG = dataECG.set_index('subject_id')
# 保留访视，本次访视时间，本访视中心电图检查时间与基线访视时间的差值三列
dataECG = dataECG.filter(items=['访视', '本次访视时间', '本访视中心电图检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataECG.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck6 = dataECG

#%%
# 提取datadict中key名称中包括“咽部充血”字符串的表格，形成一个dict
dataPharyngealCongestion = {k:v for k,v in datadict.items() if '咽部充血' in k}
# 把dataInformedConsent分别merge到dataPharyngealCongestion中的每一个df中，on='subject_id'
dataPharyngealCongestion = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataPharyngealCongestion.items()}
# 所有的表格都只保存”subject_id","咽部充血是否有检查结果？",“检查日期”和“本次访视时间”三列
dataPharyngealCongestion = {k:v.filter(items=['subject_id', '咽部充血是否有检查结果？', '检查日期', '本次访视时间']) for k,v in dataPharyngealCongestion.items()}
# 将dataPharyngealCongestion中的所有df中“咽部充血是否有检查结果？”列的值为“是”的行保留，其余行删除
dataPharyngealCongestion = {k:v[v['咽部充血是否有检查结果？'] == '是'] for k,v in dataPharyngealCongestion.items()}

# 将dataPharyngealCongestion中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataPharyngealCongestion = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataPharyngealCongestion.items()}
# 在dataPharyngealCongestion中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中咽部充血检查时间与基线访视时间的差值”
dataPharyngealCongestion = {k:v.assign(**{'本访视中咽部充血检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataPharyngealCongestion.items()}
# 给dataPharyngealCongestion中每一个df添加一个新的列，列名为“访视”，值为k
dataPharyngealCongestion = {k:v.assign(**{'访视':k}) for k,v in dataPharyngealCongestion.items()}
# 将“访视”列位置调整到第二列
dataPharyngealCongestion = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中咽部充血检查时间与基线访视时间的差值']) for k,v in dataPharyngealCongestion.items()}
# 纵向合并dataPharyngealCongestion中的所有df，形成一个大的df，以subject_id为索引
dataPharyngealCongestion = pd.concat(dataPharyngealCongestion.values(), axis=0)
# 设置subject_id为索引
dataPharyngealCongestion = dataPharyngealCongestion.set_index('subject_id')
# 保留访视，本次访视时间，本访视中咽部充血检查时间与基线访视时间的差值三列
dataPharyngealCongestion = dataPharyngealCongestion.filter(items=['访视', '本次访视时间', '本访视中咽部充血检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataPharyngealCongestion.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck7 = dataPharyngealCongestion
#%%
# 提取datadict中key名称中包括“咽部滤泡”字符串的表格，形成一个dict
dataPharyngealFollicle = {k:v for k,v in datadict.items() if '咽部滤泡' in k}
# 把dataInformedConsent分别merge到dataPharyngealFollicle中的每一个df中，on='subject_id'
dataPharyngealFollicle = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataPharyngealFollicle.items()}
# 所有的表格都只保存”subject_id","咽部滤泡是否有检查结果？",“检查日期”和“本次访视时间”三列
dataPharyngealFollicle = {k:v.filter(items=['subject_id', '咽部滤泡是否有检查结果？', '检查日期', '本次访视时间']) for k,v in dataPharyngealFollicle.items()}
# 将dataPharyngealFollicle中的所有df中“咽部滤泡是否有检查结果？”列的值为“是”的行保留，其余行删除
dataPharyngealFollicle = {k:v[v['咽部滤泡是否有检查结果？'] == '是'] for k,v in dataPharyngealFollicle.items()}
# 将dataPharyngealFollicle中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataPharyngealFollicle = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataPharyngealFollicle.items()}
# 在dataPharyngealFollicle中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中咽部滤泡检查时间与基线访视时间的差值”
dataPharyngealFollicle = {k:v.assign(**{'本访视中咽部滤泡检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataPharyngealFollicle.items()}
# 给dataPharyngealFollicle中每一个df添加一个新的列，列名为“访视”，值为k
dataPharyngealFollicle = {k:v.assign(**{'访视':k}) for k,v in dataPharyngealFollicle.items()}
# 将“访视”列位置调整到第二列
dataPharyngealFollicle = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中咽部滤泡检查时间与基线访视时间的差值']) for k,v in dataPharyngealFollicle.items()}
# 纵向合并dataPharyngealFollicle中的所有df，形成一个大的df，以subject_id为索引
dataPharyngealFollicle = pd.concat(dataPharyngealFollicle.values(), axis=0)
# 设置subject_id为索引
dataPharyngealFollicle = dataPharyngealFollicle.set_index('subject_id')

# 保留访视，本次访视时间，本访视中咽部滤泡检查时间与基线访视时间的差值三列
dataPharyngealFollicle = dataPharyngealFollicle.filter(items=['访视', '本次访视时间', '本访视中咽部滤泡检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataPharyngealFollicle.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck8 = dataPharyngealFollicle

#%%
# 提取datadict中key名称中包括“扁桃体肿大”字符串的表格，形成一个dict
dataTonsilHypertrophy = {k:v for k,v in datadict.items() if '扁桃体肿大' in k}
# 把dataInformedConsent分别merge到dataTonsilHypertrophy中的每一个df中，on='subject_id'
dataTonsilHypertrophy = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataTonsilHypertrophy.items()}
# 所有的表格都只保存”subject_id","扁桃体肿大是否有检查结果？",“检查日期”和“本次访视时间”三列
dataTonsilHypertrophy = {k:v.filter(items=['subject_id', '扁桃体肿大是否有检查结果？', '检查日期', '本次访视时间']) for k,v in dataTonsilHypertrophy.items()}
# 将dataTonsilHypertrophy中的所有df中“扁桃体肿大是否有检查结果？”列的值为“是”的行保留，其余行删除
dataTonsilHypertrophy = {k:v[v['扁桃体肿大是否有检查结果？'] == '是'] for k,v in dataTonsilHypertrophy.items()}
# 将dataTonsilHypertrophy中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataTonsilHypertrophy = {k:v.filter(items=['subject_id']).join(v.filter(items=['检查日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataTonsilHypertrophy.items()}
# 在dataTonsilHypertrophy中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中扁桃体肿大检查时间与基线访视时间的差值”
dataTonsilHypertrophy = {k:v.assign(**{'本访视中扁桃体肿大检查时间与基线访视时间的差值':v['检查日期'] - v['本次访视时间']}) for k,v in dataTonsilHypertrophy.items()}
# 给dataTonsilHypertrophy中每一个df添加一个新的列，列名为“访视”，值为k
dataTonsilHypertrophy = {k:v.assign(**{'访视':k}) for k,v in dataTonsilHypertrophy.items()}
# 将“访视”列位置调整到第二列
dataTonsilHypertrophy = {k:v.filter(items=['subject_id', '访视', '检查日期', '本次访视时间', '本访视中扁桃体肿大检查时间与基线访视时间的差值']) for k,v in dataTonsilHypertrophy.items()}
# 纵向合并dataTonsilHypertrophy中的所有df，形成一个大的df，以subject_id为索引
dataTonsilHypertrophy = pd.concat(dataTonsilHypertrophy.values(), axis=0)
# 设置subject_id为索引
dataTonsilHypertrophy = dataTonsilHypertrophy.set_index('subject_id')
# 保留访视，本次访视时间，本访视中扁桃体肿大检查时间与基线访视时间的差值三列
dataTonsilHypertrophy = dataTonsilHypertrophy.filter(items=['访视', '本次访视时间', '本访视中扁桃体肿大检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataTonsilHypertrophy.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck9 = dataTonsilHypertrophy
#%%
# 提取datadict中key名称中包括“患者自评”字符串的表格，形成一个dict
dataPatientSelfAssessment = {k:v for k,v in datadict.items() if '患者自评' in k}
# 把dataInformedConsent分别merge到dataPatientSelfAssessment中的每一个df中，on='subject_id'
dataPatientSelfAssessment = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataPatientSelfAssessment.items()}
# 所有的表格都只保存”subject_id","是否有评分结果？",“检查日期”和“本次访视时间”三列
dataPatientSelfAssessment = {k:v.filter(items=['subject_id', '是否有评分结果？', '评分日期', '本次访视时间']) for k,v in dataPatientSelfAssessment.items()}
# 将dataPatientSelfAssessment中的所有df中“是否有评分结果？”列的值为“是”的行保留，其余行删除
dataPatientSelfAssessment = {k:v[v['是否有评分结果？'] == '是'] for k,v in dataPatientSelfAssessment.items()}
# 将dataPatientSelfAssessment中的所有df中“检查日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataPatientSelfAssessment = {k:v.filter(items=['subject_id']).join(v.filter(items=['评分日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataPatientSelfAssessment.items()}
# 在dataPatientSelfAssessment中的每一个df中，使用“检查日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中患者自评检查时间与基线访视时间的差值”
dataPatientSelfAssessment = {k:v.assign(**{'本访视中患者自评检查时间与基线访视时间的差值':v['评分日期'] - v['本次访视时间']}) for k,v in dataPatientSelfAssessment.items()}
# 给dataPatientSelfAssessment中每一个df添加一个新的列，列名为“访视”，值为k
dataPatientSelfAssessment = {k:v.assign(**{'访视':k}) for k,v in dataPatientSelfAssessment.items()}
# 将“访视”列位置调整到第二列
dataPatientSelfAssessment = {k:v.filter(items=['subject_id', '访视', '评分日期', '本次访视时间', '本访视中患者自评检查时间与基线访视时间的差值']) for k,v in dataPatientSelfAssessment.items()}
# 纵向合并dataPatientSelfAssessment中的所有df，形成一个大的df，以subject_id为索引
dataPatientSelfAssessment = pd.concat(dataPatientSelfAssessment.values(), axis=0)
# 设置subject_id为索引
dataPatientSelfAssessment = dataPatientSelfAssessment.set_index('subject_id')

# 保留访视，本次访视时间，本访视中患者自评检查时间与基线访视时间的差值三列
dataPatientSelfAssessment = dataPatientSelfAssessment.filter(items=['访视', '本次访视时间', '本访视中患者自评检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataPatientSelfAssessment.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck10 = dataPatientSelfAssessment
#%%
# 提取datadict中key名称中包括“新冠”字符串的表格，形成一个dict
dataCovid19 = {k:v for k,v in datadict.items() if '新冠' in k}
# 把dataInformedConsent分别merge到dataCovid19中的每一个df中，on='subject_id'
dataCovid19 = {k:v.merge(dataInformedConsent, on='subject_id') for k,v in dataCovid19.items()}
# 所有的表格都只保存”subject_id","是否进行新冠核酸检测？",“检测日期”和“本次访视时间”三列
dataCovid19 = {k:v.filter(items=['subject_id', '是否进行新冠核酸检测？', '检测日期', '本次访视时间']) for k,v in dataCovid19.items()}
# 将dataCovid19中的所有df中“是否进行新冠核酸检测？”列的值为“是”的行保留，其余行删除
dataCovid19 = {k:v[v['是否进行新冠核酸检测？'] == '是'] for k,v in dataCovid19.items()}

# 将dataCovid19中的所有df中“检测日期”和“本次访视时间”两列全部转换成datetime格式，如果有空值，用NaT填充
dataCovid19 = {k:v.filter(items=['subject_id']).join(v.filter(items=['检测日期', '本次访视时间']).apply(pd.to_datetime, errors='coerce')) for k,v in dataCovid19.items()}
# 在dataCovid19中的每一个df中，使用“检测日期”列的值减去“本次访视时间”列的值，单位为天。得到一个新的列，列名为“本访视中新冠检查时间与基线访视时间的差值”
dataCovid19 = {k:v.assign(**{'本访视中新冠检查时间与基线访视时间的差值':v['检测日期'] - v['本次访视时间']}) for k,v in dataCovid19.items()}
# 给dataCovid19中每一个df添加一个新的列，列名为“访视”，值为k
dataCovid19 = {k:v.assign(**{'访视':k}) for k,v in dataCovid19.items()}
# 将“访视”列位置调整到第二列
dataCovid19 = {k:v.filter(items=['subject_id', '访视', '检测日期', '本次访视时间', '本访视中新冠检查时间与基线访视时间的差值']) for k,v in dataCovid19.items()}
# 纵向合并dataCovid19中的所有df，形成一个大的df，以subject_id为索引
dataCovid19 = pd.concat(dataCovid19.values(), axis=0)
# 设置subject_id为索引
dataCovid19 = dataCovid19.set_index('subject_id')
# 保留访视，本次访视时间，本访视中新冠检查时间与基线访视时间的差值三列
dataCovid19 = dataCovid19.filter(items=['访视', '本次访视时间', '本访视中新冠检查时间与基线访视时间的差值'])
# 更改列名为“访视序号”，“本次访视时间”，“与基线访视时间的差值”
dataCovid19.columns = ['访视序号', '本次访视时间', '与基线访视时间的差值']

datatimecheck11 = dataCovid19
#%%

#%%
# 纵向合并datatimecheck3-datatimecheck11，形成一个大的df，以subject_id为索引
datatimecheck = pd.concat([datatimecheck3, datatimecheck4, datatimecheck5, datatimecheck6, datatimecheck7, datatimecheck8, datatimecheck9, datatimecheck10, datatimecheck11], axis=0)
#%%
datatiime = datatimecheck.copy()
#%%
# 给datatimecheck添加一个新的列，列名为”是否异常“，值默认为空
datatiime = datatiime.assign(**{'是否异常':np.nan})
#%%
# 处理datatiime中“访视序号”列中包含字符串访视1的行
datatiime.loc[datatiime['访视序号'].str.contains('访视1'), '是否异常'] = datatiime.loc[datatiime['访视序号'].str.contains('访视1'), '与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(days=0) else np.nan)
# 处理datatiime中“访视序号”列中包含字符串访视2的行
datatiime.loc[datatiime['访视序号'].str.contains('访视2'), '是否异常'] = datatiime.loc[datatiime['访视序号'].str.contains('访视2'), '与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(days=1) else np.nan)
# 处理datatiime中“访视序号”列中包含字符串访视3的行
datatiime.loc[datatiime['访视序号'].str.contains('访视3'), '是否异常'] = datatiime.loc[datatiime['访视序号'].str.contains('访视3'), '与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(days=3) else np.nan)
# 处理datatiime中“访视序号”列中包含字符串访视4的行
datatiime.loc[datatiime['访视序号'].str.contains('访视4'), '是否异常'] = datatiime.loc[datatiime['访视序号'].str.contains('访视4'), '与基线访视时间的差值'].apply(lambda x: '异常' if x != pd.Timedelta(days=6) else np.nan)

with pd.ExcelWriter('timecheck.xlsx') as writer:
                
                datatimecheck1.to_excel(writer, sheet_name='datatimecheck1', index=True)
                datatimecheck2.to_excel(writer, sheet_name='datatimecheck2', index=True)
                datatiime.to_excel(writer, sheet_name='datatiime', index=True)
st.download_button(
                    label="点击下载",
                    data=open('timecheck.xlsx', 'rb').read(),
                    file_name='timecheck.xlsx',
                    mime='application/octet-stream')
