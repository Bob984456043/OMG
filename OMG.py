from flask import Flask,request,render_template
from pyecharts import Scatter
from prettytable import PrettyTable
import os
import math
import xlrd

app =Flask(__name__)
ControlSample=[]
KnockOutSample=[]
LogFC=[]
gene_id=[]
max_axis_value=0
#REMOTE_HOST = "https://pyecharts.github.io/assets/js"
@app.route('/')
def index():
    return  render_template('index.html')
@app.route('/credit')
def credit():
    return render_template('credit.html')
@app.route('/example')
def example():
    return render_template('example.html')
@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')
@app.route('/uploader',methods = ['GET','POST'])
def upload_file():
    global ControlSample,KnockOutSample,LogFC,gene_id
    if request.method== 'POST':
        ControlSample = []
        KnockOutSample = []
        LogFC = []
        gene_id = []
        f = request.files['file']
        f.save(f.filename)
        file_reader(f.filename)
        os.remove(f.filename)
        f.close
        scatter = Scatter_creater()
        return render_template(
            'scatter.html',
            myechart=scatter.render_embed(),
            # host=REMOTE_HOST,
            script_list=scatter.get_js_dependencies(),
            table=table_creater()
        )

def file_reader(fname):
    global ControlSample, KnockOutSample, LogFC, gene_id
    if os.path.splitext(fname)[1]==".txt":
        done = 1
        f = open(fname, 'r')
        while done:
            data = f.readline()
            if data != '':
                data = data.strip('\n')
                list = data.split('\t')
                Text_parser(list)
            else:
                done = 0
        f.close()
    elif os.path.splitext(fname)[1]==".xls" or os.path.splitext(fname)[1]==".xlsx":
        workbook = xlrd.open_workbook(fname);
        sheet = workbook.sheet_by_index(0)
        for x in range(sheet.nrows):
            list = sheet.row_values(x)
            Text_parser(list)


def Text_parser(list):
    if list[0]!='gene_id':
        if float(list[1])==0 or float(list[2])==0:
            pass
            #LogFC.append(0)
        else:
            a = math.sqrt(float(list[1]) + float(list[2]))
            Current_LogFC = round(a * math.log(float(list[2]) / float(list[1]), 2), 5)
            if Current_LogFC >= 1 or Current_LogFC <= -1:
                LogFC.append(Current_LogFC)
                gene_id.append(list[0])
                ControlSample.append(float(list[1]))
                KnockOutSample.append(float(list[2]))

def tooltip_formatter(params):
    return 'gene_id: '+params.value[3]+'<br>ControlSample: '+params.value[0]+'<br>KnockOutSample: '+params.value[1]+'<br>LogFC: '+params.value[2]
def lable_formatter(params):
    return params.value[3]
def Scatter_creater():
    max_axis_value = max(max(ControlSample),max(KnockOutSample))
    scatter = Scatter('OMG', width=800, height=600)
    scatter.add('gene',
                ControlSample,
                KnockOutSample,
                extra_name=gene_id,
                xaxis_max=max_axis_value,
                yaxis_max=max_axis_value,
                is_label_emphasis=True,
                label_formatter=lable_formatter,
                symbol_size=8,
                is_datazoom_show=True,
                is_datazoom_extra_show=True,
                datazoom_range=[0, 100],
                datazoom_extra_range=[0,100],
                datazoom_type='both',
                datazoom_extra_type='both',
                tooltip_formatter=tooltip_formatter,
                extra_data=LogFC,
                is_visualmap=True,
                visual_dimension=2,
                visual_orient='vertical',
                visual_range=[-1, 1],
                visual_range_color=['#50a3ba', '#d94e5d'],
                visual_pos=-5,
                is_toolbox_show=False
                )
    scatter.show_config()
    return scatter

def table_creater():
    t=PrettyTable()
    t.add_column('gene_id',gene_id)
    t.add_column('ControlSample',ControlSample)
    t.add_column('KnockOutSample',KnockOutSample)
    t.add_column('LogFC',LogFC)
    text=t.get_html_string(format=True,attributes={'name':'gene_table'})
    return text

if __name__ == '__main__':
    app.run(debug = True)