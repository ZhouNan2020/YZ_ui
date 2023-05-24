
for key in drug_dict.keys():
    drug_dict[key] = drug_dict[key].groupby('最终分类')
drug_dict = {key: dict(list(group)) for key, group in drug_dict.items()}