from flask import Flask, render_template, request, redirect
import requests
from bokeh.charts import Line
from bokeh.embed import file_html,components
from bokeh.resources import CDN
import dill
from cleaning import clean_ingredients

app = Flask(__name__)

def prepare_inputs(inputs, all_ingredients):
    cleaned_inputs = clean_ingredients(inputs)
    common = list(set(cleaned_inputs).intersection(all_ingredients))
    return common

def generate_prediction(inputs):
    mlbx = dill.load(open('mlbx.pkd','rb'))
    tfidf = dill.load(open('tfidf.pkd','rb'))
    svd = dill.load(open('svd.pkd','rb'))
    model = dill.load(open('model.pkd','rb'))
    y_labels = dill.load(open('y_labels.pkd','rb'))
    
    prepared_inputs = prepare_inputs(inputs, mlbx.classes_)
    
    out_of_sample_predict = model.predict(svd.transform(tfidf.transform(mlbx.transform([prepared_inputs]))))
    prediction = y_labels[out_of_sample_predict.nonzero()]
    return ', '.join(list(prediction))

@app.route('/predict', methods=['GET','POST'])
def predict():
  if request.method == 'GET':
    return render_template('predict.html')
  else:
    inputs=request.form['ingredients']
    prediction = generate_prediction(inputs)
    return render_template('prediction.html',div=prediction)

@app.route('/prediction', methods=['GET'])
def prediction():
  return render_template('prediction.html')

@app.route('/timeseries')
def timeseries():
    return render_template('reports_time_series.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/correlations')
def correlations():
    return render_template('co-occurrence.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0')



'''
params = {}
params['search']='products.name_brand:WEN+AND+products.industry_code:53'
params['count']='date_created'

def plot_time_course():
  url = 'https://api.fda.gov/food/event.json?'
  r = requests.get(url,params)
  rjson = r.json()['results']
  data = pd.DataFrame(rjson['data'])
  cols = pd.DataFrame(rjson['columns'])['name']
  data.columns = cols
  
  def convert_to_datetime(val):
    y, m, d = val.split('-')
    return pd.datetime(int(y),int(m),int(d))
  
  data['date'] = data['date'].apply(convert_to_datetime)
  data = data.set_index(['date'])
  
  t = 'Time series data for ' + app.selection['ticker']
  p = Line(data, title=t, xlabel='date', ylabel='price ($)')
  show(p)
  #app.s, app.d = components(p)
  

  return
'''