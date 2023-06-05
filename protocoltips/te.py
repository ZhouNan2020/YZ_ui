import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(800, 600))
        panel = wx.Panel(self)
        
        case_series_text = u"病例系列报告(Case Series Report)是一种在医学研究中常见的研究设计方法，其关注的是描述一组相似的临床病例。该方法涉及收集和分析一组具有相同疾病或接受相同治疗的患者的详细信息，通常包括疾病的起始，过程，治疗，以及结果。在临床研究中，病例系列报告主要用于描述和解析新的或罕见的疾病，识别新的疾病病因，或者观察新的治疗方式的疗效。尽管它无法确定因果关系，因此无法作为检验治疗效果或疾病因果关系的重要证据，但是，由于其可以提供关于疾病或治疗的详细描述，它仍然在医学研究中扮演着重要的角色。尤其是在新的疾病或治疗刚刚出现时，病例系列报告可以提供初步的，关于疾病自然病程或治疗效果的信息，为后续更加系统和严格的研究提供依据。"
        
        case_series_label = wx.StaticText(panel, label=case_series_text, pos=(20, 20), size=(720, -1))
        case_series_label.Wrap(720)
        case_series_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        # 设置行距为 1.5 倍
        if hasattr(case_series_label, 'SetDoubleLineSpacing'):
            case_series_label.SetDoubleLineSpacing(60)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(case_series_label, proportion=1, flag=wx.EXPAND)
        panel.SetSizer(sizer)
        
app = wx.App()
frame = MyFrame(None, "Text Line Spacing Example")
frame.Show()
app.MainLoop()
