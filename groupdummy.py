
import pandas as pd
import numpy as np

file = pd.ExcelFile('优替德隆-(20230515）(1).xlsx')
rawdata = pd.ExcelFile(file)



dummysheet = ''

dummycol = ''

dummied_sheet = rawdata.parse(dummysheet)
dummied_sheet = pd.get_dummies(dummied_sheet, columns=[dummycol])

dummied_sheet = dummied_sheet.groupby('subject_id').sum().reset_index()
dummied_sheet_cols = [col for col in dummied_sheet.columns if col.startswith(dummycol)]
dummied_sheet_cols.append('subject_id')
dummied_sheet = dummied_sheet[dummied_sheet_cols]

tab6combinedata = pd.concat([rawdata.parse(sheet_name) for sheet_name in rawdata.sheet_names], axis=1, join='outer')
tab6combinedata = tab6combinedata.loc[:,~tab6combinedata.columns.duplicated()]
tab6combinedata = pd.merge(tab6combinedata, dummied_sheet, how='outer', on='subject_id')
def classify(df):
    df['最终分类'] = ''
    columns = dummied_sheet.columns
    for i in range(len(df)):
        if all(pd.isna(df.loc[df.index[i], col]) for col in columns):
            df.loc[df.index[i], '最终分类'] = '未知'
        else:
            for col in columns:
                if df.loc[df.index[i], col] != 0:
                    df.loc[tab6combinedata.index[i], '最终分类'] += col + '+'
            df.loc[df.index[i], '最终分类'] = df.loc[df.index[i], '最终分类'][:-1]
    return df
tab6combinedata = classify(tab6combinedata)
datadict = {}
for i in range(len(tab6combinedata)):
    if tab6combinedata.loc[tab6combinedata.index[i], '最终分类'] not in datadict:
        datadict[tab6combinedata.loc[tab6combinedata.index[i], '最终分类']] = tab6combinedata.iloc[[i]]
    else:
        datadict[tab6combinedata.loc[tab6combinedata.index[i], '最终分类']] = pd.concat([datadict[tab6combinedata.loc[tab6combinedata.index[i], '最终分类'] ], tab6combinedata.iloc[[i]]], axis=0)
        datadict[tab6combinedata.loc[tab6combinedata.index[i], '最终分类']] = datadict[tab6combinedata.loc[tab6combinedata.index[i], '最终分类']].replace(dummycol, '', regex=True)


writer = pd.ExcelWriter('dummiegroup.xlsx')
for key in datadict.keys():
    key = key.replace('[','').replace(']','').replace(',','和').replace('"','').replace("'","")
    datadict[key].to_excel(writer, sheet_name=key, index=False)
writer.save