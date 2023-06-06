import wx
import pandas as pd

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#aed0ee")
        self.SetIcon(wx.Icon('icon.png', wx.BITMAP_TYPE_PNG))
        self.font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.button_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text_font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.dict = {}

        self.upload_button = wx.Button(self.panel, label="上传文件", pos=(20, 20), size=(100, 30))
        self.upload_button.SetFont(self.font)
        self.upload_button.Bind(wx.EVT_BUTTON, self.on_upload)

        self.notebook = wx.Notebook(self.panel, pos=(20, 70), size=(760, 500))
        self.notebook.SetFont(self.button_font)
        self.panel.Bind(wx.EVT_SIZE, self.on_resize)

        self.case_series_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.case_series_panel, "病例系列研究")
        self.show_case_series_report()
        self.show_case_series_dropdowns()


        self.cross_sectional_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.cross_sectional_panel, "横断面研究")
        self.show_cross_sectional_report()
        
        self.nested_case_control_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.nested_case_control_panel, "巢式病例-对照研究")

    def on_resize(self, event):
        size = self.panel.GetSize()
        self.notebook.SetSize((size[0]-40, size[1]-90))


    def on_upload(self, event):
        with wx.FileDialog(self, "选择文件", wildcard="Excel files (*.xls;*.xlsx)|*.xls;*.xlsx",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            path = fileDialog.GetPath()
            try:
                self.file = pd.ExcelFile(path)
                for sheet_name in self.file.sheet_names:
                    self.dict[sheet_name] = self.file.parse(sheet_name)
            except Exception as e:
                wx.MessageBox(f"无法读取文件: {e}", "错误", wx.OK | wx.ICON_ERROR)
 

    
    def show_case_series_report(self):
        case_series_text = "病例系列报告是一种在医学研究中常见的研究设计方法，其关注的是描述一组相似的临床病例。该方法涉及收集和分析一组具有相同疾病或接受相同治疗的患者的详细信息，通常包括疾病的起始，过程，治疗，以及结果。在临床研究中，病例系列报告主要用于描述和解析新的或罕见的疾病，识别新的疾病病因，或者观察新的治疗方式的疗效。尽管它无法确定因果关系，因此无法作为检验治疗效果或疾病因果关系的重要证据，但是，由于其可以提供关于疾病或治疗的详细描述，它仍然在医学研究中扮演着重要的角色。尤其是在新的疾病或治疗刚刚出现时，病例系列报告可以提供初步的，关于疾病自然病程或治疗效果的信息，为后续更加系统和严格的研究提供依据。"
        case_series_label = wx.StaticText(self.case_series_panel, label=case_series_text, pos=(20, 20), size=(720, -1))
        case_series_label.Wrap(720)
        case_series_label.SetFont(self.text_font)
        if hasattr(case_series_label, 'SetDoubleLineSpacing'):
            case_series_label.SetDoubleLineSpacing(1.5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(case_series_label, proportion=1, flag=wx.EXPAND)
        self.case_series_panel.SetSizer(sizer)
    
    def show_case_series_dropdowns(self):
        
        
        keys = list(self.dict.keys())
        self.key_dropdown = wx.ComboBox(self.case_series_panel, pos=(20, 200), size=(200, 30), choices=keys, style=wx.CB_READONLY)
        self.key_dropdown.Bind(wx.EVT_COMBOBOX, self.on_key_select)
        
        self.col_dropdown = wx.ComboBox(self.case_series_panel, pos=(240, 200), size=(200, 30), style=wx.CB_READONLY)
        self.col_dropdown.Bind(wx.EVT_COMBOBOX, self.on_col_select)
        
        self.group_dropdown = wx.ComboBox(self.case_series_panel, pos=(460, 200), size=(200, 30), style=wx.CB_READONLY)
        self.group_dropdown.Bind(wx.EVT_COMBOBOX, self.on_group_select)
        
    def on_key_select(self, event):
        self.CaseSerieskey = self.key_dropdown.GetValue()
        df = self.dict[self.CaseSerieskey]
        cols = list(df.columns)
        self.col_dropdown.SetItems(cols)
        
    def on_col_select(self, event):
        self.CaseSeriescol = self.col_dropdown.GetValue()
        df = self.dict[self.CaseSerieskey]
        groups = list(df[self.CaseSeriescol].unique())
        self.group_dropdown.SetItems(groups)
        
    def on_group_select(self, event):
        self.CaseSeriesgroup = self.group_dropdown.GetValue()
        df = self.dict[self.CaseSerieskey]
        group_df = df.groupby(self.CaseSeriescol).get_group(self.CaseSeriesgroup)
        print(group_df)

    



 
    def show_cross_sectional_report(self):
        cross_sectional_text = "横断面研究是一种在流行病学中常见的研究设计方法，其关注的是在某一时间点上，对一个群体的某一特定特征或变量进行测量。该方法涉及收集和分析一组具有相同特征或变量的患者的详细信息，通常包括患者的年龄，性别，疾病状态，以及其他相关因素。在流行病学研究中，横断面研究主要用于描述和解析某一特定疾病或疾病群体的流行病学特征，如患病率，死亡率，以及相关因素的分布情况。尽管它无法确定因果关系，因此无法作为检验治疗效果或疾病因果关系的重要证据，但是，由于其可以提供关于疾病或治疗的详细描述，它仍然在医学研究中扮演着重要的角色。"
        cross_sectional_label = wx.StaticText(self.cross_sectional_panel, label=cross_sectional_text, pos=(20, 20), size=(720, -1))
        cross_sectional_label.Wrap(720)
        cross_sectional_label.SetFont(self.text_font)
        if hasattr(cross_sectional_label, 'SetDoubleLineSpacing'):
            cross_sectional_label.SetDoubleLineSpacing(1.5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(cross_sectional_label, proportion=1, flag=wx.EXPAND)
        self.cross_sectional_panel.SetSizer(sizer)




    

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame(None, "选题助手")
    frame.Show()
    app.MainLoop()



