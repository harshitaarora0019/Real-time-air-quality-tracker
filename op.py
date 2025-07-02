import streamlit as st  # Streamlit for building the web app interface
import requests          # To make HTTP requests for APIs
from gtts import gTTS    # Google Text-to-Speech for converting text to audio
import pygame            # Pygame for playing audio
import os                # For file path operations
import tempfile          # To create temporary files
import base64            # For encoding and decoding data, commonly used with audio in Streamlit


# Init
pygame.mixer.init()
st.set_page_config(page_title="Real-Time Air Quality Tracker", layout="wide")

# Language and 'state'
language = "en"
st.session_state.setdefault("speech_on", True)
st.session_state.setdefault("spoken_main", False)

# 🎤 Safe speech
def speak(text):
    if not st.session_state.speech_on:
        return
    temp_path = None
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
            tts.save(temp_path)
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(30)
        pygame.mixer.music.unload()
    except Exception as e:
        st.warning(f"Speech error: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

# 🎨 Theme selector
st.sidebar.title("🎨 Theme")
theme = st.sidebar.radio("Choose Theme", ["Light", "Dark"], key="theme_selector")

# 🌄 Background only in Light mode
if theme == "Light":
    def get_base64_of_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    image_path = "pic.avif"
    base64_img = get_base64_of_image(image_path)

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/avif;base64,{base64_img}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

# 🌈 Theme CSS
if theme == "Dark":
    st.markdown("""
        <style>
        .card {
            background-color: #1f1f1f;
            color: white;
            border-radius: 10px;
            padding: 0.8rem;
            margin: 0.4rem;
            box-shadow: 0 0 8px rgba(255,255,255,0.2);
            font-size: 14px;
        }
        .section-title, .aqi-header, h1, h3, h4, p, div {
            color: white !important;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin-top: 1.2rem;
            margin-bottom: 0.8rem;
        }
        .aqi-header {
            font-size: 24px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .card {
            background-color: white;
            color: black;
            border-radius: 10px;
            padding: 0.8rem;
            margin: 0.4rem;
            box-shadow: 0 0 6px rgba(0,0,0,0.1);
            font-size: 14px;
        }
        .section-title, .aqi-header, h1, h3, h4, p, div {
            color: black !important;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin-top: 1.2rem;
            margin-bottom: 0.8rem;
        }
        .aqi-header {
            font-size: 24px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# 📢 Headline
st.markdown(f"<h1 style='text-align: center;'>🌍 Real-Time Air Quality Tracker</h1>", unsafe_allow_html=True)

# 🎧 Greeting
if "greeted" not in st.session_state:
    st.session_state.greeted = True
    greet_msg = "Hello Human! I'm your Real-Time Air Quality Tracker. Please enter your city to get the air quality report."
    speak(greet_msg)

# Sidebar inputs
st.sidebar.markdown("### 🏙 Enter Your City")
city = st.sidebar.text_input("City", placeholder="Type your city here")

st.sidebar.title("🤖 AirBot")
st.sidebar.markdown("### Ask me anything about air quality:")
airbot_input = st.sidebar.text_input("Question", label_visibility="visible")

# Chatbot logic
if airbot_input:
    response = "Sure I Tell You:"
    user_q = airbot_input.lower()
    if "pm2.5" in user_q:
        response += " PM2.5 is safe below 12 micrograms per cubic meter."
    elif "pm10" in user_q:
        response += " PM10 is safe under 54 micrograms per cubic meter."
    elif "co" in user_q:
        response += " CO is safe below 4000 micrograms per cubic meter."
    elif "no2" in user_q:
        response += " NO2 is safe when under 50 micrograms per cubic meter."
    elif "aqi" in user_q:
        response += " AQI means Air Quality Index."
    elif "plant" in user_q:
        response += " Try Areca Palm, Snake Plant, or Money Plant."
    elif "safe" in user_q:
        response += " Stay indoors and wear masks during high AQI."
    else:
        response += " Monitor AQI and limit outdoor activity in high pollution."
    st.sidebar.success(response)
    speak(response)

# API key
API_KEY = "686d487ae00c37f15964bc0bcba6b953"

# Pollutant details
def pollutant_details(label):
    info = {
        "PM2.5": ("Can penetrate lungs and bloodstream.", "Asthma, lung cancer.", "Use air purifiers, stay indoors."),
        "PM10": ("Irritates nose/throat.", "Allergies, bronchitis.", "Keep windows closed, clean indoor air."),
        "CO": ("Reduces oxygen supply.", "Headaches, dizziness.", "Ventilate home, avoid smoke."),
        "NO2": ("Inflames airways.", "Asthma, infections.", "Use air-purifying plants, reduce vehicles.")
    }
    return info.get(label, ("", "", ""))

# Plants
def recommended_plants():
    return [
        ("🌿 Areca Palm", "Releases moisture and removes toxins."),
        ("🪴 Snake Plant", "Produces oxygen at night."),
        ("🍀 Money Plant", "Filters air toxins and boosts oxygen.")
    ]

# Main display
if city:
    try:
        geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}").json()
        if geo:
            lat, lon = geo[0]['lat'], geo[0]['lon']

            weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
            temp = weather_data['main']['temp']
            wind = weather_data['wind']['speed']
            humidity = weather_data['main']['humidity']

            air_data = requests.get(f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}").json()
            comp = air_data['list'][0]['components']
            aqi = air_data['list'][0]['main']['aqi']

            aqi_quality = {
                1: "Good – Air quality is satisfactory.",
                2: "Fair – Air quality is acceptable.",
                3: "Moderate – May affect sensitive people.",
                4: "Poor – Health effects possible.",
                5: "Very Poor – Everyone may experience effects."
            }

            st.markdown(f"<h3 class='aqi-header'>🌫 AQI in {city.title()}: {aqi}</h3>", unsafe_allow_html=True)
            st.markdown(f"<div class='card'><p><b>🩺 AQI Quality:</b> {aqi_quality.get(aqi, 'Unknown')}</p></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-title'>🌤 Current Weather Conditions</div>", unsafe_allow_html=True)
            weather_cols = st.columns(3)
            with weather_cols[0]:
                st.markdown(f"<div class='card'><h4>🌡 Temperature</h4><p>{temp:.1f} °C</p></div>", unsafe_allow_html=True)
            with weather_cols[1]:
                st.markdown(f"<div class='card'><h4>🌬 Wind Speed</h4><p>{wind:.1f} m/s</p></div>", unsafe_allow_html=True)
            with weather_cols[2]:
                st.markdown(f"<div class='card'><h4>💧 Humidity</h4><p>{humidity:.0f} %</p></div>", unsafe_allow_html=True)

            pollutant_quality = {
                "pm2_5": [(0, 12, "Good"), (12.1, 35, "Moderate"), (35.1, 55, "Unhealthy"), (55.1, 1000, "Hazardous")],
                "pm10": [(0, 54, "Good"), (55, 154, "Moderate"), (155, 1000, "Unhealthy")],
                "co": [(0, 4000, "Safe"), (4001, 100000, "High")],
                "no2": [(0, 50, "Safe"), (51, 1000, "High")]
            }

            def get_quality(pollutant, value):
                for low, high, label in pollutant_quality[pollutant]:
                    if low <= value <= high:
                        return label
                return "Unknown"

            st.markdown("<div class='section-title'>🔬 Pollutant Levels</div>", unsafe_allow_html=True)
            speech_lines = [
                f"The temperature is {temp:.1f} degrees Celsius.",
                f"Wind speed is {wind:.1f} meters per second.",
                f"Humidity is {humidity:.0f} percent."
            ]
            cols = st.columns(4)
            for idx, (label, key) in enumerate(zip(["PM2.5", "PM10", "CO", "NO2"], ["pm2_5", "pm10", "co", "no2"])):
                value = comp[key]
                quality = get_quality(key, value)
                with cols[idx]:
                    st.markdown(f"""
                        <div class='card'>
                        <h3>{label}</h3>
                        <p>Level: {value:.2f} μg/m³</p>
                        <p>Status: <b>{quality}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                speech_lines.append(f"{label} is {value:.2f} micrograms per cubic meter and is considered {quality}.")

            st.markdown("<div class='section-title'>🩺 Health Recommendations</div>", unsafe_allow_html=True)
            cols2 = st.columns(4)
            for idx, label in enumerate(["PM2.5", "PM10", "CO", "NO2"]):
                health, disease, solution = pollutant_details(label)
                with cols2[idx]:
                    st.markdown(f"""
                        <div class='card'>
                        <h4>{label}</h4>
                        <p><b>Health Impact:</b> {health}<br>
                        <b>Disease Risk:</b> {disease}<br>
                        <b>Recommended Solution:</b> {solution}</p>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div class='section-title'>🌿 Recommended Indoor Plants</div>", unsafe_allow_html=True)
            cols3 = st.columns(3)
            plant_names = []
            for idx, (plant, desc) in enumerate(recommended_plants()):
                with cols3[idx % 3]:
                    st.markdown(f"<div class='card'><h4>{plant}</h4><p>{desc}</p></div>", unsafe_allow_html=True)
                    plant_names.append(plant.split(" ")[1])

            full_speech = f"Here is the air quality for {city}. " + " ".join(speech_lines)
            full_speech += " You can keep indoor plants like " + ", ".join(plant_names) + "."

            if st.session_state.get("last_city") != city:
                st.session_state.spoken_main = False
                st.session_state.last_city = city

            if not st.session_state.spoken_main:
                speak(full_speech)
                st.session_state.spoken_main = True

    except:
        st.error("Could not fetch data. Please check the city name.")
