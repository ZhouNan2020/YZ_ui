# 使用tkinter创建
import docx
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, LEFT
from tkinter import messagebox
from matplotlib import font_manager
from matplotlib import pyplot as plt
from tkinter import font as tkFont
## 导入sklearn的Imputer包，用于填充缺失值
from sklearn.impute import SimpleImputer as Imputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, Binarizer, KBinsDiscretizer, StandardScaler, MinMaxScaler
import threading



font = font_manager.FontProperties(fname='simhei.ttf', size=10)
parameters = {'xtick.labelsize': 17,
              'ytick.labelsize': 17,
              'font.family': 'SimHei',
              'axes.unicode_minus': False}
plt.rcParams.update(parameters)
plt.style.use('ggplot')


# 定义一个窗口
window = tk.Tk()
window.title('优卓医药科技')
window.geometry('1200x800')
window.resizable(True, True)
window.configure(background="#89c3eb")
tabControl = ttk.Notebook(window)

        
tab1 = tk.Frame(bg='#d5ebe1', relief='ridge', borderwidth=2)
tab2 = tk.Frame(bg='#d5ebe1', relief='ridge', borderwidth=2)
tab3 = tk.Frame(bg='#d5ebe1', relief='ridge', borderwidth=2)     
tab4 = tk.Frame(bg='#d5ebe1', relief='ridge', borderwidth=2)


 

global raw_data
raw_data = pd.DataFrame()



# 定义一个文件上传类，通过tkinter的filedialog.askopenfilename()方法获取文件路径，存储于self.file_path,然后使用openpyxl读取文件，将所有的sheet合并为一个表格，重新编制索引，重复列只保存一个

  
class UploadFile():
    def __init__(self):
        self.file_path = None

    def parse(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            t = threading.Thread(target=self.read_file)
            t.start()

    def read_file(self):
        try:
            sheets = pd.ExcelFile(self.file_path)
            dfs = [sheets.parse(sheet_name) for sheet_name in sheets.sheet_names]
            merged_df = pd.concat(dfs, axis=1)
# 将所有列横向合并到一个DataFrame中
            merged_cols_df = merged_df.iloc[:, ~merged_df.columns.duplicated()]
            global raw_data
            raw_data = merged_cols_df
            messagebox.showinfo('上传完成', '上传完成')
        except Exception as e:
            messagebox.showerror('错误', str(e))

          

tab1_button_1 = tk.Button(tab1, text='上传数据', font=('Arial', 12), command=UploadFile().parse)
tab1_button_1.place(relx=0.01, rely=0.01, relwidth=0.1, relheight=0.05)

    
    
        

 
 
#  
 
# 定义一个上传数据tab1_button_1，调用上传文件
tab1_button_1 = tk.Button(tab1, text='上传数据', font=('Arial', 12), command=UploadFile().parse)
tab1_button_1.place(relx=0.01, rely=0.01, relwidth=0.1, relheight=0.05)


 
class ShowData():
    def __init__(self):
        self.file = None
        self.tree = None
        self.scrollbar_y = None
        self.scrollbar_x = None

    def show_data(self):
        self.tree = ttk.Treeview(tab1, show='headings', columns=raw_data.columns)
        self.tree.place(relx=0.01, rely=0.1, relwidth=0.98, relheight=0.8)
        self.scrollbar_y = ttk.Scrollbar(tab1, orient='vertical', command=self.tree.yview)
        self.scrollbar_y.place(relx=0.99, rely=0.1, relwidth=0.01, relheight=0.8)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_x = ttk.Scrollbar(tab1, orient='horizontal', command=self.tree.xview)
        self.scrollbar_x.place(relx=0.01, rely=0.91, relwidth=0.98, relheight=0.01)
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.tree.column('#0', width=0, stretch='no')
        for i in range(len(raw_data.columns)):
            if i < len(self.tree['columns']):
                self.tree.column(i, width=100, anchor='center')
                self.tree.heading(i, text=raw_data.columns[i])
        for i in range(len(raw_data)):
            if len(list(raw_data.iloc[i])) >= len(raw_data.columns):
                self.tree.insert('', i, values=list(raw_data.iloc[i]))
        self.tree.bind('<Button-1>', self.show_data)
        for i in range(len(raw_data.columns)):
            if i < len(self.tree['columns']):
                self.tree.column(i, width=100, anchor='center')
                self.tree.heading(i, text=raw_data.columns[i])
        for i in range(len(raw_data)):
            if len(list(raw_data.iloc[i])) >= len(raw_data.columns):
                self.tree.insert('', i, values=list(raw_data.iloc[i]))
        self.tree.bind('<Button-1>', self.show_data)





    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i in range(len(raw_data)):
            self.tree.insert('', i, values=list(raw_data.iloc[i]))

    def thread_show_data(self):
        t = threading.Thread(target=self.show_data)
        t.start()

tab1_button_2 = tk.Button(tab1, text='展示数据', font=('Arial', 12), command=ShowData().thread_show_data)
tab1_button_2.place(relx=0.12, rely=0.01, relwidth=0.1, relheight=0.05)








                
      
    

 
 
# 定义一个预处理方法类，在构造函数中增加self.preprocessed_data，用于存储预处理后的数据，
class DataPreprocess(ShowData):
    def __init__(self):
        super().__init__()
        self.preprocessed_data = None

        # 定义一个函数，对分类变量执行编码，使用sklearn.preprocessing中的LabelEncoder方法，额外加一个实参col_name，处理后的col_name列将被concat到self.preprocessed_data中

    def label_encoder(self, col_name):
        le = LabelEncoder()
        le.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat(
            [self.preprocessed_data, pd.DataFrame(le.transform(raw_data[col_name]), columns=[col_name])], axis=1)

        # 对分类变量执行独热编码，使用sklearn.preprocessing中的OneHotEncoder方法，额外给出一个实参col_name

    def one_hot_encoder(self, col_name):
        ohe = OneHotEncoder()
        ohe.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat([self.preprocessed_data,
                                            pd.DataFrame(ohe.transform(raw_data[col_name]).toarray(),
                                                         columns=ohe.get_feature_names())], axis=1)

        # 对分类变量执行二值化，使用sklearn.preprocessing中的Binarizer方法，额外给出一个实参data

    def binarizer(self, col_name):
        binarizer = Binarizer()
        binarizer.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat(
            [self.preprocessed_data, pd.DataFrame(binarizer.transform(raw_data[col_name]), columns=[col_name])],
            axis=1)

        # 分类变量缺失值插补，求出data中的众数，使用sklearn.preprocessing中的Imputer方法，为缺失值插补众数，额外给出一个实参data

    def missingValueOfCategoricalVariable(self, col_name):
        imputer = Imputer(strategy='most_frequent')
        imputer.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat(
            [self.preprocessed_data, pd.DataFrame(imputer.transform(raw_data[col_name]), columns=[col_name])], axis=1)

        # 如果偏度绝对值大于1，则使用中位数插补，如果偏度绝对值小于1，则使用均值插补，使用sklearn.preprocessing中的Imputer方法，额外给出一个实参data

    def continuousVariableMissingValue(self, col_name):
        skew = raw_data[col_name].skew()
        # 如果skew的绝对值大于1，则使用中位数插补
        if abs(skew) > 1:
            imputer = Imputer(strategy='median')
            imputer.fit(raw_data[col_name])
            self.preprocessed_data = pd.concat(
                [self.preprocessed_data, pd.DataFrame(imputer.transform(raw_data[col_name]), columns=[col_name])],
                axis=1)
        # 如果skew的绝对值小于或等于1，则使用均值插补
        else:
            imputer = Imputer(strategy='mean')
            imputer.fit(raw_data[col_name])
            self.preprocessed_data = pd.concat(
                [self.preprocessed_data, pd.DataFrame(imputer.transform(raw_data[col_name]), columns=[col_name])],
                axis=1)
        # 连续变量离散化，使用sklearn.preprocessing中的KBinsDiscretizer方法，额外给出一个实参data，将data中的数据进行离散化，离散化的方式为等频离散化

    def continuousVariableDiscretization(self, col_name):
        k_bins_discretizer = KBinsDiscretizer()
        k_bins_discretizer.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat([self.preprocessed_data,
                                            pd.DataFrame(k_bins_discretizer.transform(raw_data[col_name]),
                                                         columns=[col_name])], axis=1)

        # 连续变量标准化，使用sklearn.preprocessing中的StandardScaler方法，额外给出一个实参data，将data中的数据进行标准化

    def continuousVariableStandardization(self, col_name):
        standard_scaler = StandardScaler()
        standard_scaler.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat(
            [self.preprocessed_data, pd.DataFrame(standard_scaler.transform(raw_data[col_name]), columns=[col_name])],
            axis=1)

        # 连续变量归一化，使用sklearn.preprocessing中的MinMaxScaler方法，额外给出一个实参data，将data中的数据进行归一化

    def continuousVariableNormalization(self, col_name):
        min_max_scaler = MinMaxScaler()
        min_max_scaler.fit(raw_data[col_name])
        self.preprocessed_data = pd.concat(
            [self.preprocessed_data, pd.DataFrame(min_max_scaler.transform(raw_data[col_name]), columns=[col_name])],
            axis=1)


# 定义一个checkbutton类
class CheckButton(DataPreprocess):
    def __init__(self):
        super().__init__()

    # 定义名为连续变量缺失值插补的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def continuous_missing_check(self, frame, ):
        self.continuous_missing = tk.IntVar()
        self.continuous_missing_checkbutton = tk.Checkbutton(frame, text='连续变量缺失值插补',
                                                             variable=self.continuous_missing, onvalue=1, offvalue=0)
        self.continuous_missing_checkbutton.pack(side='left')

    # 定义名为分类变量缺失值插补的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def category_missing_check(self, frame, ):
        self.category_missing = tk.IntVar()
        self.category_missing_checkbutton = tk.Checkbutton(frame, text='分类变量缺失值插补',
                                                           variable=self.category_missing, onvalue=1, offvalue=0)
        self.category_missing_checkbutton.pack(side='left')

    # 定义名为连续变量异常值处理的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令

    # 定义名为连续变量离散化的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def continuous_discretization_check(self, frame, ):
        self.continuous_discretization = tk.IntVar()
        self.continuous_discretization_checkbutton = tk.Checkbutton(frame, text='连续变量离散化',
                                                                    variable=self.continuous_discretization, onvalue=1,
                                                                    offvalue=0)
        self.continuous_discretization_checkbutton.pack(side='left')

    # 定义名为连续变量标准化的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def continuous_standardization_check(self, frame, ):
        self.continuous_standardization = tk.IntVar()
        self.continuous_standardization_checkbutton = tk.Checkbutton(frame, text='连续变量标准化',
                                                                     variable=self.continuous_standardization,
                                                                     onvalue=1, offvalue=0)
        self.continuous_standardization_checkbutton.pack(side='left')

    # 定义名为标签编码的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def label_encoding_check(self, frame, ):
        self.label_encoding = tk.IntVar()
        self.label_encoding_checkbutton = tk.Checkbutton(frame, text='标签编码', variable=self.label_encoding,
                                                         onvalue=1, offvalue=0)
        self.label_encoding_checkbutton.pack(side='left')

    # 定义名为独热编码的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def one_hot_encoding_check(self, frame, ):
        self.one_hot_encoding = tk.IntVar()
        self.one_hot_encoding_checkbutton = tk.Checkbutton(frame, text='独热编码', variable=self.one_hot_encoding,
                                                           onvalue=1, offvalue=0)
        self.one_hot_encoding_checkbutton.pack(side='left')

    # 定义名为"二元化“的checkbutton，放在实参frame中，位置为row行，column列，选中时，值为1，未选中时，值为0，暂时不调用命令
    def binarization_check(self, frame, ):
        self.binarization = tk.IntVar()
        self.binarization_checkbutton = tk.Checkbutton(frame, text='二元化', variable=self.binarization, onvalue=1,
                                                       offvalue=0)
        self.binarization_checkbutton.pack(side='left')

    # 定义一个判断以上方法是否被选中的函数，如果被选中（intvar返回1），则调用DataPreprocess类中的相应函数
    def preprocess(self, column):
        if self.continuous_missing.get() == 1:
            self.continuousVariableMissingValue(column)
        if self.category_missing.get() == 1:
            self.missingValueOfCategoricalVariable(column)
        if self.continuous_discretization.get() == 1:
            self.continuousVariableDiscretization(column)
        if self.continuous_standardization.get() == 1:
            self.continuousVariableStandardization(column)
        if self.label_encoding.get() == 1:
            self.label_encoder(column)
        if self.one_hot_encoding.get() == 1:
            self.one_hot_encoder(column)
        if self.binarization.get() == 1:
            self.binarizer(column)


# 定义一个“执行预处理”的类，放在实参frame中，继承自CheckButton类
class PreprocessButton(CheckButton):
    def __init__(self):
        super().__init__()

    # 定义一个按钮名为执行预处理，放在frame中，位置为row行最末列，命令为self.preprocess函数,给一个column实参
    def preprocess_button_func(self, frame, column):
        self.preprocess_button = tk.Button(frame, text='执行预处理', command=lambda: self.preprocess(column))
        # grid格式放置在row行，最末列（不是column列），sticky='e'表示靠右
        self.preprocess_button.pack(side='right')


# 定义一个数据类型判断类，继承自ShowData类，用于判断数据类型
class DataType(PreprocessButton):
    def __init__(self):
        super().__init__()

    # 从self.file中取出一个列名所对应的数据，判断数据类型，，给一个实参col_name
    def data_type(self, col_name):
        data = raw_data[col_name]
        # 如果数据类型为为float或int，返回continuousVariable
        if data.dtype == 'float64' or data.dtype == 'int64':
            return 'continuousVariable'
        # 如果数据类型为object，返回categoryVariable
        elif data.dtype == 'object':
            return 'categoryVariable'
        # 如果数据类型为其他，返回other
        else:
            return 'other'

    # 定义一个函数，调用data_type函数
    def data_type_judge(self, col_name):
        return self.data_type(col_name)




# 定义一个排列数据的类，继承自DataType类
class ArrangeData(DataType, CheckButton):
    def __init__(self):
        super().__init__()

    # 定义一个函数，遍历数据中所有列名
    def arrange_data(self):
        for col_name in raw_data.columns:
            # 定义一个frame，在tab2中放置，靠左pack
            frame = tk.Frame(tab2)
            # 将列名放在frame中，靠左pack
            tk.Label(frame, text=col_name).pack(side='left')
            # 使用列名调用data_type_judge函数，如果返回值为'continuousVariable'
            if self.data_type_judge(col_name) == 'continuousVariable':
                # 调用continuous_missing函数，frame=frame
                self.continuous_missing_check(frame=frame)
                # 调用continuous_discretization_check函数，frame=frame
                self.continuous_discretization_check(frame=frame)
                # continuous_standardization_check函数，frame=frame
                self.continuous_standardization_check(frame=frame)
                # 调用preprocess_button函数，frame=frame，column=col_name
                self.preprocess_button_func(frame=frame, column=col_name)
            elif self.data_type_judge(col_name) == 'categoryVariable':
                # 调用category_missing_check函数，frame=frame
                self.category_missing_check(frame=frame)
                # 调用label_encoding_check函数，frame=frame
                self.label_encoding_check(frame=frame)
                # 调用one_hot_encoding_check函数，frame=frame
                self.one_hot_encoding_check(frame=frame)
                # 调用binarization_check函数，frame=frame
                self.binarization_check(frame=frame)
                # 调用preprocess_button函数，frame=frame，column=col_name
                self.preprocess_button_func(frame=frame, column=col_name)
            else:
                # 使用label写“复杂数据类型，请在其他软件中进行预处理后重新上传”
                tk.Label(frame, text='复杂数据类型，请在其他软件中进行预处理后重新上传').pack(side='left')


 



# 定义一个结束数据预处理类，继承自ArrangeData类
class EndDataPreProces(ArrangeData):
    def __init__(self):
        super().__init__()

    def replace_columns(self):
        for col in self.preprocessed_data.columns:
            if col in raw_data.columns:
                raw_data[col] = self.preprocessed_data[col]
            else:
                raw_data = pd.concat([raw_data, self.preprocessed_data[col]], axis=1)

      
# 

tabControl.add(tab1, text='数据预览')
tabControl.add(tab2, text='数据预处理')
tabControl.add(tab3, text='报告生成')
tabControl.add(tab4, text='关于')
 

tabControl.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.98)


window.mainloop()








 


    
