 
# Importing tkinter and commonly used widgets
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import pandas as pd


raw_data = pd.read_excel('C:\Users\Zhou N\Desktop\YTDL2023002-EDC导出数据（20230510 14点47分40）.xlsx')



import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import KBinsDiscretizer
from scipy.stats import skew

class DataPreprocessing(tk.Frame):
    def __init__(self, parent, raw_data):
        tk.Frame.__init__(self, parent)
        self.raw_data = raw_data
        self.create_widgets()

    def create_widgets(self):
        row = 0
        self.checkbuttons = {}
        for col_name in self.raw_data.columns:
            col_type = self.raw_data[col_name].dtype
            col_label = tk.Label(self, text=col_name)
            col_label.grid(row=row, column=0)

            if np.issubdtype(col_type, np.number):
                self.create_numeric_checkbuttons(row, col_name)
            elif col_type == 'object':
                self.create_object_checkbuttons(row, col_name)
            else:
                error_label = tk.Label(self, text="不可识别的数据类型")
                error_label.grid(row=row, column=1)

            row += 1

        process_button = tk.Button(self, text="开始处理", command=self.process_data)
        process_button.grid(row=row, column=0, columnspan=2)

    def create_numeric_checkbuttons(self, row, col_name):
        var1 = tk.BooleanVar()
        var2 = tk.BooleanVar()
        var3 = tk.BooleanVar()

        cb1 = tk.Checkbutton(self, text="连续变量缺失值插补", variable=var1)
        cb2 = tk.Checkbutton(self, text="连续变量标准化", variable=var2)
        cb3 = tk.Checkbutton(self, text="连续变量离散化", variable=var3)

        cb1.grid(row=row, column=1)
        cb2.grid(row=row, column=2)
        cb3.grid(row=row, column=3)

        self.checkbuttons[col_name] = (var1, var2, var3)

    def create_object_checkbuttons(self, row, col_name):
        var1 = tk.BooleanVar()
        var2 = tk.BooleanVar()
        var3 = tk.BooleanVar()

        cb1 = tk.Checkbutton(self, text="分类变量缺失值插补", variable=var1)
        cb2 = tk.Checkbutton(self, text="分类变量编码", variable=var2)
        cb3 = tk.Checkbutton(self, text="独热编码", variable=var3)

        cb1.grid(row=row, column=1)
        cb2.grid(row=row, column=2)
        cb3.grid(row=row, column=3)

        self.checkbuttons[col_name] = (var1, var2, var3)

    def process_data(self):
        for col_name, (var1, var2, var3) in self.checkbuttons.items():
            col_type = self.raw_data[col_name].dtype
            if np.issubdtype(col_type, np.number):
                self.process_numeric_column(col_name, var1.get(), var2.get(), var3.get())
            elif col_type == 'object':
                self.process_object_column(col_name, var1.get(), var2.get(), var3.get())

    def process_numeric_column(self, col_name, impute, standardize, discretize):
        if impute:
            skewness = skew(self.raw_data[col_name].dropna())
            if abs(skewness) > 1:
                imputer = SimpleImputer(strategy='median')
            else:
                imputer = SimpleImputer(strategy='mean')
            self.raw_data[col_name] = imputer.fit_transform(self.raw_data[[col_name]])

        if standardize:
            scaler = StandardScaler()
            self.raw_data[col_name] = scaler.fit_transform(self.raw_data[[col_name]])

        if discretize:
            discretizer = KBinsDiscretizer()
            self.raw_data[col_name] = discretizer.fit_transform(self.raw_data[[col_name]])

    def process_object_column(self, col_name, impute, encode, one_hot):
        if impute:
            imputer = SimpleImputer(strategy='most_frequent')
            self.raw_data[col_name] = imputer.fit_transform(self.raw_data[[col_name]])

        if encode:
            encoder = LabelEncoder()
            self.raw_data[col_name] = encoder.fit_transform(self.raw_data[col_name])

        if one_hot:
            one_hot_encoder = OneHotEncoder()
            one_hot_data = one_hot_encoder.fit_transform(self.raw_data[[col_name]])
            # Add one_hot_data to the DataFrame (omitted for brevity)

# Create the main window
root = tk.Tk()
root.title("数据预处理")

# Create the notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill=tk.BOTH)

# Create the DataPreprocessing frame and add it to the notebook
data_preprocessing_frame = DataPreprocessing(notebook, raw_data)
notebook.add(data_preprocessing_frame, text="数据预处理")

root.mainloop()