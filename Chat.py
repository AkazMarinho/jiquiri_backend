from sklearn.linear_model import LinearRegression # pip install scikit-learn
import re
import pandas as pd
import numpy as np

def convertJsonInDf(registro):

    registro = registro[0]

    data = {
        'hr': list(range(6, 19)),  
        'air': [registro['air_humidity'][str(i).zfill(2)] for i in range(6, 19)],  
        'soil': [registro['soil_humidity'][str(i).zfill(2)] for i in range(6, 19)],  
        'temp': [registro['temperature'][str(i).zfill(2)] for i in range(6, 19)],  
    }

    df = pd.DataFrame(data)

    df["hr"] = df["hr"].astype(int)

    return df

def predict_for_hour(registros, hora, variavel, name):

    print(registros)

    data = []    
    for registro in registros:
        hora_str = str(hora).zfill(2)
        if hora_str in registro[variavel]:
            data.append({
                'day_number': registro['id'],
                'value': registro[variavel][hora_str]
            })

    df = pd.DataFrame(data)

    print(df)

    df.rename(columns={variavel: name}, inplace=True)

    return df

def identificar_intencao(pergunta, dados, paginate):
    df = convertJsonInDf(dados)
    try:
        # pergunta para medias diarias
        if "média" in pergunta.lower() or "media" in pergunta.lower():
            if "umidade" in pergunta.lower() and "ar" in pergunta.lower():
                media_air = round(df["air"].mean(), 2)
                return f"Umidade do ar: {media_air}%"
            if "umidade" in pergunta.lower() and "solo" in pergunta.lower():
                media_soil = round(df["soil"].mean(), 2)
                return f"Umidade do solo: {media_soil}%"
            if "temperatura" in pergunta.lower() or "temperaturas" in pergunta.lower():
                media_temp = round(df["temp"].mean(), 2)
                return f"Temperatura: {media_temp}°C"
            
        if any(palavra in pergunta.lower() for palavra in ["max", "maximo", "máximo", "maxima", "máxima", "maior"]):
            if "umidade" in pergunta.lower() and "ar" in pergunta.lower():
                return f"Maior valor de Umidade do ar: {df['air'].min()}%"
            if "umidade" in pergunta.lower() and "solo" in pergunta.lower():
                return f"Maior valor de Umidade do solo: {df['soil'].min()}%"
            if "temperatura" in pergunta.lower() or "temperaturas" in pergunta.lower():
                return f"Maior valor de Temperatura: {df['temp'].min()}°C"
            
        if any(palavra in pergunta.lower() for palavra in ["min", "minimo", "minímo", "minima", "miníma", "menor"]):
            if "umidade" in pergunta.lower() and "ar" in pergunta.lower():
                return f"Menor valor de Umidade do ar: {df['air'].max()}%"
            if "umidade" in pergunta.lower() and "solo" in pergunta.lower():
                return f"Menor valor de Umidade do solo: {df['soil'].max()}%"
            if "temperatura" in pergunta.lower() or "temperaturas" in pergunta.lower():
                return f"Menor valor de Temperatura: {df['temp'].max()}°C"


        match = re.search(r"(\d{1,2})", pergunta)
        hora = int(match.group(1))
        if hora > 5 and hora <= 18:
            if any(palavra in pergunta.lower() for palavra in ["amanhã", "amanha", "futuro", "futuros"]):
                if "umidade" in pergunta.lower() and "ar" in pergunta.lower():
                    df = predict_for_hour(paginate, hora, "air_humidity", "air")
                    X = df[['day_number']]
                    y = df['value']
                    model = LinearRegression().fit(X, y)
                    next_day = np.array([[df['day_number'].max() + 1]])
                    prediction = model.predict(next_day)[0]
                    return f"Para o horário {hora}:00, o valor estimado de Umidade do ar para o dia de amanhã é: {round(prediction, 2)}%"

                if "umidade" in pergunta.lower() and "solo" in pergunta.lower():
                    df = predict_for_hour(paginate, hora, "soil_humidity", 'soil')
                    X = df[['day_number']]
                    y = df['value']
                    model = LinearRegression().fit(X, y)
                    next_day = np.array([[df['day_number'].max() + 1]])
                    prediction = model.predict(next_day)[0]
                    return f"Para o horário {hora}:00, o valor estimado de Umidade do solo para o dia de amanhã é: {round(prediction, 2)}%"
                
                if "temperatura" in pergunta.lower() or "temperaturas" in pergunta.lower():
                    df = predict_for_hour(paginate, hora, "temperature", 'temp')
                    X = df[['day_number']]
                    y = df['value']
                    model = LinearRegression().fit(X, y)
                    next_day = np.array([[df['day_number'].max() + 1]])
                    prediction = model.predict(next_day)[0]
                    return f"Para o horário {hora}:00, o valor estimado de Temperatura para o dia de amanhã é: {round(prediction, 2)}%"
                
            if any(palavra in pergunta.lower() for palavra in ["hoje", "hj"]):
                if "umidade" in pergunta.lower() and "ar" in pergunta.lower():      
                    return f"Para o horário {hora}:00, a Umidade do ar para hoje é: {round(df.loc[df['hr'] == hora, 'air'].iloc[0].item(), 2)}%"
                if "umidade" in pergunta.lower() and "solo" in pergunta.lower():             
                    return f"Para o horário {hora}:00, a Umidade do solo para hoje é: {round(df.loc[df['hr'] == hora, 'air'].iloc[0].item(), 2)}%"
                if "temperatura" in pergunta.lower() or "temperaturas" in pergunta.lower():             
                    return f"Para o horário {hora}:00, a Temperatura para hoje é: {round(df.loc[df['hr'] == hora, 'air'].iloc[0].item(), 2)}%"
        else:
            return "Hora fora do periodo de dados"

        return "Desculpe, não entendi sua pergunta. Verifique erros de ortografia, e caso o problema persista, talvez sua pergunta não esteja relacionado ao tema🐶"
    
    except Exception as e:
        return "Desculpe, não entendi sua pergunta. Verifique erros de ortografia, e caso o problema persista, talvez sua pergunta não esteja relacionado ao tema🐶"
        
