from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from dotenv import load_dotenv
from Chat import identificar_intencao
from Structure import sctructureHour, sctructureJson
import os

load_dotenv()
database_url = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.sort_keys = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class General(db.Model): # colocar em outro arquivo
    __tablename__ = 'general_registration'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    air_humidity_id = db.Column(db.Integer, db.ForeignKey('air_humidity.id'), unique=True)
    soil_humidity_id = db.Column(db.Integer, db.ForeignKey('soil_humidity.id'), unique=True)
    temperature_id = db.Column(db.Integer, db.ForeignKey('temperature.id'), unique=True)

    air_humidity = db.relationship('AirHumidity', uselist=False, foreign_keys=[air_humidity_id])
    soil_humidity = db.relationship('SoilHumidity', uselist=False, foreign_keys=[soil_humidity_id])
    temperature = db.relationship('Temperature', uselist=False, foreign_keys=[temperature_id])

class AirHumidity(db.Model):
    __tablename__ = 'air_humidity'
    
    id = db.Column(db.Integer, primary_key=True)
    general_id = db.Column(db.Integer, db.ForeignKey('general_registration.id'), unique=True)
    
    h01 = db.Column(db.Float)
    h02 = db.Column(db.Float)
    h03 = db.Column(db.Float)
    h04 = db.Column(db.Float)
    h05 = db.Column(db.Float)
    h06 = db.Column(db.Float)
    h07 = db.Column(db.Float)
    h08 = db.Column(db.Float)
    h09 = db.Column(db.Float)
    h10 = db.Column(db.Float)
    h11 = db.Column(db.Float)
    h12 = db.Column(db.Float)
    h13 = db.Column(db.Float)

class SoilHumidity(db.Model):
    __tablename__ = 'soil_humidity'
    
    id = db.Column(db.Integer, primary_key=True)
    general_id = db.Column(db.Integer, db.ForeignKey('general_registration.id'), unique=True)
    
    h01 = db.Column(db.Float)
    h02 = db.Column(db.Float)
    h03 = db.Column(db.Float)
    h04 = db.Column(db.Float)
    h05 = db.Column(db.Float)
    h06 = db.Column(db.Float)
    h07 = db.Column(db.Float)
    h08 = db.Column(db.Float)
    h09 = db.Column(db.Float)
    h10 = db.Column(db.Float)
    h11 = db.Column(db.Float)
    h12 = db.Column(db.Float)
    h13 = db.Column(db.Float)

class Temperature(db.Model):
    __tablename__ = 'temperature'
    
    id = db.Column(db.Integer, primary_key=True)
    general_id = db.Column(db.Integer, db.ForeignKey('general_registration.id'), unique=True)
    
    h01 = db.Column(db.Float)
    h02 = db.Column(db.Float)
    h03 = db.Column(db.Float)
    h04 = db.Column(db.Float)
    h05 = db.Column(db.Float)
    h06 = db.Column(db.Float)
    h07 = db.Column(db.Float)
    h08 = db.Column(db.Float)
    h09 = db.Column(db.Float)
    h10 = db.Column(db.Float)
    h11 = db.Column(db.Float)
    h12 = db.Column(db.Float)
    h13 = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    if not file:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    df = pd.read_csv(file)

    expected_columns = {'air', 'soil', 'temp'}
    if not expected_columns.issubset(df.columns.str.strip()):
        return jsonify({'error': f'O CSV deve conter as colunas: {", ".join(expected_columns)}'}), 400

    general = General()
    db.session.add(general)
    db.session.commit()

    air_humidity_data = {f'h{i+1:02d}': df['air'][i] for i in range(13)}
    soil_humidity_data = {f'h{i+1:02d}': df['soil'][i] for i in range(13)}
    temperature_data = {f'h{i+1:02d}': df['temp'][i] for i in range(13)}

    air_humidity = AirHumidity(general_id=general.id, **air_humidity_data)
    soil_humidity = SoilHumidity(general_id=general.id, **soil_humidity_data)
    temperature = Temperature(general_id=general.id, **temperature_data)
    
    db.session.add_all([air_humidity, soil_humidity, temperature])
    db.session.commit()

    general.air_humidity_id = air_humidity.id
    general.soil_humidity_id = soil_humidity.id
    general.temperature_id = temperature.id
    db.session.commit()

    return jsonify({'message': 'Arquivo processado com sucesso', 'registro_id': general.id}), 201

@app.route('/all_records', methods=['GET'])
def get_registros():
    registros = General.query.all()
    
    resultado = []
    for registro in registros:

        resultado.append(sctructureJson(registro))
    
    return jsonify(resultado)
    
@app.route('/specific_day', methods=['GET'])
def get_day():
    date_str = request.args.get('date')

    if date_str:
        try:
            date_filter = datetime.strptime(date_str, "%Y-%m-%d").date()
            registros = General.query.filter(db.func.date(General.data) == date_filter).all()

            if not registros:
                return jsonify({"error": "Day not found!"}), 404
            
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400
    else:
        return jsonify({"error": "O parâmetro 'date' é obrigatório."}), 400

    resultado = [sctructureJson(registro) for registro in registros]
    return jsonify(resultado)

@app.route('/pagination')
def get_items():
    page = request.args.get('page', 2, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    paginated_items = General.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "page": paginated_items.page,
        "per_page": paginated_items.per_page,
        "total": paginated_items.total,
        "data": [ sctructureJson(registro) for registro in paginated_items.items]
    })

@app.route('/predict', methods=['GET'])
def predictAirHumidity():

    columnHR = request.args.get("column", "h01")
    dados = AirHumidity.query.order_by(AirHumidity.id.desc()).limit(20).all()
    df = pd.DataFrame([(d.id, d.h01, d.h02, d.h03, d.h04, d.h05, d.h06, d.h07, d.h08, d.h09, d.h10, d.h11, d.h12, d.h13) for d in dados],
                      columns=["id", "h01", "h02", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10", "h11", "h12", "h13"])

    series = df[columnHR]
    if len(series) < 20:
        return jsonify({"error": "Número de registros insuficiente para o modelo ARIMA"})

    model = ARIMA(series, order=(5, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=1)

    previsao = {
        "predict": forecast.values[0]
    }

    return jsonify(previsao)

@app.route('/chatbot_ask', methods=['GET'])
def ask_bot():
    question = request.args.get('question', '')
    data = General.query.order_by(General.id.desc()).first()
    data_ow = [sctructureHour(data)]

    paginated_items = General.query.paginate(page=1, per_page=10, error_out=False)
    paginated_data = [sctructureHour(registro) for registro in paginated_items.items]

    resposta = identificar_intencao(question, data_ow, paginated_data)
    return jsonify({"answer": resposta})

if __name__ == '__main__':
    app.run(debug=True)
