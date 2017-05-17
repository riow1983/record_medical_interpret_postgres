from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from flask_heroku import Heroku

import numpy as np
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from functools import reduce
from io import BytesIO

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/english'
heroku = Heroku(app)
app.secret_key = 'some_secret'
db = SQLAlchemy(app)


# Create our database model(database name: english)
class Report(db.Model):
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True)
    personnel = db.Column(db.Text) 
    starttime = db.Column(db.DateTime) 
    endtime = db.Column(db.DateTime) 
    client = db.Column(db.Text) 
    section = db.Column(db.Text) 
    patient = db.Column(db.Text) 
    country = db.Column(db.Text) 
    summary = db.Column(db.Text)

    def __init__(self, personnel, starttime, endtime, client, section, patient, country, summary):
        self.personnel = personnel
        self.starttime = starttime
        self.endtime = endtime
        self.client = client
        self.section = section
        self.patient = patient
        self.country = country
        self.summary = summary

    def __repr__(self):
        return '<Personnel %r>' % self.personnel




@app.route('/')
def home():
    return render_template('home.html')

@app.route('/enternew')
def new_student():
    return render_template('report.html')

@app.route('/addrec', methods = ['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        #conn = sql.connect("database.db")
        #conn.row_factory = sql.Row
        #cur = conn.cursor()
        try:
            personnel = request.form['personnel']
            starttime = request.form['start']
            endtime = request.form['end']
            client = request.form['client']
            section = request.form['section']
            patient = request.form['pt']
            country = request.form['country']
            summary = request.form['summary']

            #cur.execute("INSERT INTO report (personnel,starttime,endtime,client,section,patient,country,summary) VALUES (?,?,?,?,?,?,?,?)", (personnel,starttime,endtime,client,section,patient,country,summary))
            #conn.commit()
            reg = User(personnel, starttime, endtime, client, section, patient, country, summary)
            db.session.add(reg)
            db.session.commit()
            msg = "Record successfully added"

        except:
            #conn.rollback()
            db.session.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg = msg)
            #conn.close()
            db.session.close()

@app.route('/list')
def list():
    #conn = sql.connect("database.db")
    #conn.row_factory = sql.Row

    #cur = conn.cursor()
    #cur.execute("SELECT * FROM report")
    #rows = cur.fetchall(); 
    rows = Report.query.all()
    return render_template("list.html", rows=rows)
    #conn.close()
    db.session.close()


@app.route('/data')
def data():
    return render_template("data.html")


@app.route('/fig', methods = ['POST', 'GET'])
def fig():
    if request.method == 'POST':
        #conn = sql.connect("database.db")
        #sqlstring = "SELECT * FROM report"
        #df = pd.read_sql(sqlstring,conn)
        df = pd.read_sql(Report.query.all())
    
        df["time_required"] = pd.to_datetime(df["endtime"]) - pd.to_datetime(df["starttime"])
        df["time_required(m)"] = df["time_required"].astype('timedelta64[m]')
        df["month"] = df["starttime"].apply(lambda x:x[:7])
        df = df[["personnel","month","time_required(m)"]]

        start = str(request.form['start'])
        end = str(request.form['end'])

        df = df[(df["month"]>=start)&(df["month"]<=end)]
        df = df.groupby(["month","personnel"]).sum()
        df = df.reset_index()

        res = []
        for month in set(df["month"]):
            tmp = df[df["month"]==month]
            tmp = tmp.drop("month",1)
            tmp = tmp.set_index("personnel").T
            tmp["month"] = month
            res.append(tmp)
        
        try:
            dfc = reduce(lambda x,y: pd.concat([x,y]), res)
            
            dfc = dfc.set_index("month")
            dfc = dfc.fillna(0)
        
            dfc = dfc.sort_index()
            col = dfc.columns.tolist()
            rows = dfc.index.tolist()
            data = dfc
            columns = col
            rows = rows

            # Get some pastel shades for the colors
            colors = plt.cm.BuPu(np.linspace(0, 0.5, len(rows)))
            n_rows = len(data)

            index = np.arange(len(columns)) + 0.3
            bar_width = 0.4

            # Initialize the vertical-offset for the stacked bar chart.
            y_offset = np.array([0.0] * len(columns))

            plt.figure()

            # Plot bars and create text labels for the table
            cell_text = []
            for row in range(n_rows):
                plt.bar(index, data.iloc[row,:], bar_width, bottom=y_offset, color=colors[row])
                y_offset = y_offset + data.iloc[row,:]
                cell_text.append(['%s' % x for x in data.iloc[row,:]])
            # Reverse colors and text labels to display the last value at the top.
            #colors = colors[::-1]
            #cell_text.reverse()

            # Add a table at the bottom of the axes
            the_table = plt.table(cellText=cell_text,
                                  rowLabels=rows,
                                  rowColours=colors,
                                  colLabels=columns,
                                  loc='bottom')

            # Adjust layout to make room for the table:
            plt.subplots_adjust(left=0.2, bottom=0.2)

            plt.ylabel("Time Required (m)")
            #plt.yticks(values * value_increment, ['%d' % val for val in values])
            plt.xticks([])
            plt.title('English Translation Support')

            ##image = cStringIO.StringIO()
            image = BytesIO()
            plt.savefig(image, format='png')
            image.seek(0)
            return send_file(image, attachment_filename="image.png", as_attachment=True)
        except:
            flash("There is no data.")
            return redirect(url_for('data'))
            


        #conn.close()
        db.session.close()


    





if __name__ == '__main__':
	app.run(debug = True, host='0.0.0.0')
