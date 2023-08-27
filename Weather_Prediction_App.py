import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import tempfile
import gtts
from datetime import datetime

# Set your OpenWeatherMap API key here
API_KEY = "e61ca93041e9bcb8a6e4be25bca0e972"

# Function to get weather data from OpenWeatherMap API
def get_weather_data(city_name):
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}appid={API_KEY}&q={city_name}"
        response = requests.get(complete_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        try:
            error_message = response.json()["message"]
        except Exception:
            error_message = "An error occurred while fetching weather data."
        st.error(f"Error: {error_message}")
        return None

st.title("Weather Prediction Chatbot")

# Welcome message
st.write("Welcome to the Weather Prediction Chatbot!")

# Display current date and time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.subheader("Current Date and Time")
st.write(current_time)

# User input
city_input = st.text_input("Enter a city name:")
submit_button = st.button("Submit")

# Create a chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Handle user input and weather prediction
if submit_button and city_input:
    weather_data = get_weather_data(city_input)

    if weather_data is not None and weather_data["cod"] == 200:
        weather_description = weather_data["weather"][0]["description"].capitalize()
        temperature = (weather_data["main"]["temp"]) - 273.15
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
    
        st.subheader("Weather Information")
        st.write(f"City: {city_input}")
        
        # Display weather icon
        icon_code = weather_data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        icon_image = Image.open(BytesIO(requests.get(icon_url).content))
        st.image(icon_image, caption="Weather Icon", width=100)
        
        st.write(f"Weather: {weather_description}")
        st.write(f"Temperature: {round(temperature, 2)} °C")
        st.write(f"Humidity: {humidity}%")
        st.write(f"Wind Speed: {wind_speed} m/s")
    
        # Add user message to chat history
        user_message = f"Tell me the weather in {city_input}"
        st.session_state.chat_history.append({"sender": "You", "text": user_message})
    
        # Prepare chatbot response
        chatbot_response = (
            f"City: {city_input}, "
            f"Weather: {weather_description}, "
            f"Temperature: {round(temperature, 2)} °C, "
            f"Humidity: {humidity}%, "
            f"Wind Speed: {wind_speed} m/s"
        )
    
        # Add chatbot message to history
        st.session_state.chat_history.append({"sender": "Chatbot", "text": chatbot_response})

# Display chat history
st.subheader("Chat History")

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    st.text(f"{message['sender']}: {message['text']}")

# Text-to-speech button
if st.session_state.chat_history and st.session_state.chat_history[-1]["sender"] == "Chatbot" and st.button("Read Chatbot Response"):
    tts = gtts.gTTS(text=st.session_state.chat_history[-1]["text"], lang='en')
    audio_file = tempfile.NamedTemporaryFile(delete=False)
    tts.save(audio_file.name)
    st.audio(audio_file.name, format='audio/wav')
