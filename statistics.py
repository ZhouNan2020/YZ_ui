#%%
import numpy as np
import pandas as pd
#%%
# 使用pandas读取raw_data
df = pd.ExcelFile("raw_data.xlsx")
#%%
 
# 从df中提取出所有sheet名称中包含字符串“生命体征”的sheet，将这些sheet另存为多个新的独立df，所有的新df放入一个dict中
dfs_dict = {}
for sheet_name in df.sheet_names:
    if "生命体征" in sheet_name:
        dfs_dict[sheet_name] = pd.read_excel("raw_data.xlsx", sheet_name=sheet_name)

#%%
 
# 遍历dfs_dict中的所有df，将这些df中列名为”subject_id“的列设置为索引
for key in dfs_dict:
    dfs_dict[key].set_index("subject_id", inplace=True)


#%%
 
for key in dfs_dict:
    dfs_dict[key].replace("ND", np.nan, inplace=True)

#%%

 
for key in dfs_dict:
    dfs_dict[key].drop(columns=["是否进行生命体征检查", "检查日期"], inplace=True)


#%%
 
# 遍历dfs_dict中的所有列，将不同df中名称相同的列横向合并成一个新的df，存储于一个新的字典中，横向合并以现有索引为参考。
merged_dict = {}
for key in dfs_dict:
    for col in dfs_dict[key].columns:
        if col not in merged_dict:
            merged_dict[col] = dfs_dict[key][col]
        else:
            merged_dict[col] = pd.concat([merged_dict[col], dfs_dict[key][col]], axis=1)

#%%
#  
# 遍历merged_dict中的所有df，求出这些df中每一行的行平均值（mean with row），求出的平均值列作为一个新的列，横向合并在df右侧。在所有的df中，np.nan的项在求平均值时不会被作为分母的计数。
for column, merged_df in merged_dict.items():

    # 计算每一行的均值（不包含nan值，nan值不计入分母）

    row_means = merged_df.apply(lambda x: pd.to_numeric(x, errors='coerce').sum() / pd.to_numeric(x, errors='coerce').count() if pd.to_numeric(x, errors='coerce').count() != 0 else float('nan'), axis=1)

    # 将均值插入到df的右侧末尾

    merged_df.insert(len(merged_df.columns), str(column) + "_mean", row_means)
    
#%%
# 保存为一个excel，命名为“vitalsigns.xlsx”
with pd.ExcelWriter("vitalsigns.xlsx") as writer:
    for key in merged_dict:
        merged_dict[key].to_excel(writer, sheet_name=key)
