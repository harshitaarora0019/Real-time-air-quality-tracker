import pyttsx3
import requests

# 🔊 Speak + Print in English
def speak_and_print(text):
    lines = text.split('\n')
    for line in lines:
        print(line)
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(line)
        engine.runAndWait()

# 🧠 AQI Status Mapping
def get_aqi_status(aqi):
    status_map = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    return status_map.get(aqi, "Unknown")

# 🩺 Health message per pollutant
def health_message(value, pollutant):
    if pollutant == "PM2.5":
        if value <= 12:
            return "PM2.5 levels are good and safe."
        elif value <= 35.4:
            return "PM2.5 levels are moderate; may cause asthma and lung irritation."
        elif value <= 55.4:
            return "PM2.5 levels are unhealthy for sensitive groups; decreased lung function possible."
        else:
            return "PM2.5 levels are hazardous; risk of heart attacks and lung cancer increases."

    elif pollutant == "PM10":
        if value <= 54:
            return "PM10 levels are good and safe."
        elif value <= 154:
            return "PM10 levels are moderate; may cause asthma and respiratory symptoms."
        elif value <= 254:
            return "PM10 levels are unhealthy for sensitive groups; decreased lung function possible."
        else:
            return "PM10 levels are hazardous; increased risk of lung diseases."

    elif pollutant == "CO":
        if value <= 4000:
            return "CO levels are good and safe."
        elif value <= 10000:
            return "High CO exposure may cause headaches and dizziness."
        else:
            return "Very high CO levels; risk of serious cardiovascular effects."

    elif pollutant == "NO2":
        if value <= 53:
            return "NO2 levels are good and safe."
        elif value <= 100:
            return "NO2 levels may cause respiratory inflammation and reduce lung function."
        else:
            return "High NO2 exposure increases risk of respiratory diseases and asthma."

    else:
        return "No health information available."

# ⚕️ Disease & Recommended Solution
def disease_and_solution(pollutant, value):
    if pollutant == "PM2.5":
        if value <= 12:
            return "No significant health risks.", "Enjoy fresh outdoor air."
        elif value <= 35.4:
            return "Mild risk of asthma or lung irritation.", "Use a mask outdoors and avoid heavy exercise outside."
        elif value <= 55.4:
            return "Risk of reduced lung function in sensitive individuals.", "Use an air purifier and avoid outdoor exposure."
        else:
            return "High risk of heart disease and lung cancer.", "Wear a high-quality mask, stay indoors, and use air purifiers."

    elif pollutant == "PM10":
        if value <= 54:
            return "No major health concern.", "Keep indoor air ventilated."
        elif value <= 154:
            return "Risk of allergies and respiratory issues.", "Use dust filters and avoid outdoor activity."
        else:
            return "Higher risk of lung disease and infections.", "Install purifiers and avoid polluted areas."

    elif pollutant == "CO":
        if value <= 4000:
            return "No serious health threat.", "Ensure proper ventilation indoors."
        elif value <= 10000:
            return "Can cause headache and dizziness.", "Avoid exposure to smoke or car exhausts."
        else:
            return "Risk of cardiovascular and neurological effects.", "Seek medical attention and increase indoor air flow."

    elif pollutant == "NO2":
        if value <= 53:
            return "Safe exposure level.", "No specific actions needed."
        elif value <= 100:
            return "Risk of respiratory irritation.", "Avoid industrial areas and use air filters."
        else:
            return "High risk of asthma and chronic lung diseases.", "Stay indoors and use advanced air filtration systems."

    else:
        return "Data not available.", "No solution found."

# 🌿 Indoor Plant Suggestion
def suggest_plants(aqi):
    if aqi == 1:
        return ["Money Plant", "Aloe Vera"]
    elif aqi == 2:
        return ["Areca Palm", "Spider Plant"]
    elif aqi == 3:
        return ["Snake Plant", "Peace Lily"]
    elif aqi == 4:
        return ["Bamboo Palm", "Rubber Plant"]
    elif aqi == 5:
        return ["English Ivy", "Areca Palm", "Use Air Purifier"]
    else:
        return []

def plant_summary():
    return (
        "These plants help reduce indoor air pollutants, improve oxygen levels, "
        "and protect you from respiratory problems, asthma, and allergies."
    )

# 🌍 Fetch AQI and Pollutant Data
def get_air_quality(city_name, api_key):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
    location_data = requests.get(geo_url).json()
    if not location_data:
        return None, "City not found!"

    lat = location_data[0]['lat']
    lon = location_data[0]['lon']

    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    air_data = requests.get(air_url).json()
    aqi = air_data['list'][0]['main']['aqi']
    components = air_data['list'][0]['components']

    return {
        "aqi": aqi,
        "pm2_5": components['pm2_5'],
        "pm10": components['pm10'],
        "co": components['co'],
        "no2": components['no2'],
        "lat": lat,
        "lon": lon
    }, "Success"

# 🌦️ Fetch Wind Speed and Humidity
def get_weather(lat, lon, api_key):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    weather_data = requests.get(weather_url).json()
    if 'wind' in weather_data and 'humidity' in weather_data['main']:
        wind_speed = weather_data['wind'].get('speed', 0)
        humidity = weather_data['main'].get('humidity', 0)
        return wind_speed, humidity
    else:
        return None, None

# 🚀 Main Function
def main():
    speak_and_print("Hello! I am a Real-Time Air Quality Tracker.\n")
    
    api_key = "686d487ae00c37f15964bc0bcba6b953"
    speak_and_print("Please enter your city name:")
    city = input("🏙️ Enter City Name: ")

    data, msg = get_air_quality(city, api_key)
    if not data:
        speak_and_print(f"❌ Error: {msg}\nSorry! I could not fetch the data.")
        return

    aqi = data['aqi']
    status = get_aqi_status(aqi)
    wind_speed, humidity = get_weather(data['lat'], data['lon'], api_key)

    speak_and_print(f"📍 City: {city}")
    speak_and_print(f"AQI: {aqi} - {status}")
    speak_and_print(f"The Air Quality Index in {city} is {aqi}, which means the air quality is categorized as '{status}'.\n")

    for pollutant in ["PM2.5", "PM10", "CO", "NO2"]:
        value = data[pollutant.lower().replace(".", "_")]
        health = health_message(value, pollutant)
        disease, solution = disease_and_solution(pollutant, value)

        paragraph = (
            f"{pollutant} level in {city} is {value} micrograms per cubic meter.\n"
            f"Health Impact: {health}\n"
            f"Disease Risk: {disease}\n"
            f"Recommended Solution: {solution}\n"
        )
        speak_and_print(paragraph)

    if wind_speed is not None:
        wind_para = (
            f"Wind speed in {city} is {wind_speed} meters per second.\n"
            f"This helps disperse pollutants and improve air quality.\n"
        ) 
        speak_and_print(wind_para)

    if humidity is not None:
        humidity_para = (
            f"The humidity level in {city} is {humidity} percent.\n"
            f"High humidity allows pollutants to stay suspended in the air longer, increasing the risk of breathing difficulties.\n"
        )
        speak_and_print(humidity_para)

    plants = suggest_plants(aqi)
    if plants:
        plants_text = ", ".join(plants)
        speak_and_print(
            f"To improve indoor air quality, you can keep the following plants: {plants_text}.\n"
            f"{plant_summary()}"
        )

# 🏁 Run Program
if __name__ == "__main__":
    main()
