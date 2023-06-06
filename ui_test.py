
from flask import Flask, render_template, request

app = Flask(__name__)

class MyApp:
    def __init__(self):
        self.file = None
        self.sheetdict = {}
        self.sheet_selected = None
        self.col_selected = []
        self.df_final = None
        self.dfdict = {}
        self.sheet_names = None
        self.sheet_names_tab3 = []
        self.index = None
        self.sheet_names_tab4 = None
        self.selectedsheet = {}
        self.tab3colnames = []

    def sidebar(self):
        print('tab2')
        # Define your sidebar here

    def tabintro(self):
        print('tab1')
        # Define the tabintro content here

    def tab1(self):
        print('tab2')
        # Define the tab1 content here

    def tab2(self):
        print('tab2')
        # Define the tab2 content here

    def tab3(self):
        print('tab2')

        # Define the tab3 content here

    def tab4(self):
        print('tab2')
        # Define the tab4 content here

    def tab5(self):
        print('tab2')
        # Define the tab5 content here

    def tab6(self):
        print('tab2')
        # Define the tab6 content here

    def tab7(self):
        print('tab2')
        # Define the tab7 content here

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    my_app.tabintro()
    return render_template("about.html")

@app.route("/preview")
def preview():
    my_app.tab1()
    return render_template("preview.html")

@app.route("/filter")
def filter():
    my_app.tab2()
    return render_template("filter.html")

@app.route("/group")
def group():
    my_app.tab3()
    return render_template("group.html")

@app.route("/experiment")
def experiment():
    my_app.tab4()
    return render_template("experiment.html")

@app.route("/count")
def count():
    my_app.tab5()
    return render_template("count.html")

@app.route("/dummy")
def dummy():
    my_app.tab6()
    return render_template("dummy.html")

@app.route("/drug")
def drug():
    my_app.tab7()
    return render_template("drug.html")

if __name__ == "__main__":
    my_app = MyApp()
    app.run(debug=True)

# jinja2.exceptions.TemplateNotFound
# The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.


