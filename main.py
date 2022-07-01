from flask import Flask, render_template, request, redirect
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///weather_by_city.db'
db = SQLAlchemy(app)

url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=1cd8cde3cf001cdd86c8f0ef64f9c65a'

class City(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), nullable=False, unique=True)

   def __repr__(self):
      return self.name

def current_weather(r):
   weather = {
      'city': r['name'],
      'temperature': str(int(r['main']['temp'])) + u'\N{DEGREE SIGN}' + 'C',
      'feels_like': str(int(r['main']['feels_like'])) + u'\N{DEGREE SIGN}' + 'C',
      'icon': r['weather'][0]['icon'],
      'date': datetime.fromtimestamp(r["dt"]).strftime('%d %B, %Y'),
      'description': r['weather'][0]['description'].capitalize(),
      'humidity': str(r['main']['humidity']) + '%',
      'wind': r['wind']['speed'],
      'visibility': r['visibility'],
      'sunrise': datetime.fromtimestamp(r["sys"]['sunrise']).strftime('%-I:%-M %p'),
      'sunset': datetime.fromtimestamp(r["sys"]['sunset']).strftime('%-I:%-M %p')
   }
   return weather

@app.route('/delete', methods = ['POST'])
def clear():
   City.query.delete()
   db.session.commit()
   return redirect('/')

@app.route('/', methods = ['POST', 'GET'])
def index():
   if request.method == 'POST':
      return redirect(f'/{request.form.get("city")}')
   else:
      return render_template('home.html')


@app.route('/about', methods = ['POST', 'GET'])
def about():
   if request.method == 'POST':
      return redirect(f'/{request.form.get("city")}')
   else:
      return render_template('about.html')

@app.route('/history', methods = ['POST', 'GET'])
def history():
   if request.method == 'POST':
      return redirect(f'/{request.form.get("city")}')
   else:
      cities = City.query.all()
      weathers_data = []
      for city in cities:
         weathers_data.append(current_weather( requests.get(url.format(city)).json()) )
      return render_template('history.html', weathers = weathers_data)

@app.route('/<string:city>', methods = ['POST', 'GET'])
def weather(city):
   if request.method == 'POST':
      new_city = request.form.get('city')
      return redirect(f'/{new_city}')
   else:
      r = requests.get(url.format(city)).json()

      if r['cod'] == '404':
         return render_template('404.html')

      if db.session.query(City).filter(City.name==city).first() == None:
         new_city = City(name=city)
         db.session.add(new_city)
         db.session.commit()

      return render_template('weather.html', weather = current_weather(r))

if __name__ == '__main__':
   app.run(debug = True)


