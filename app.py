
# ---------------------------------------------------------------------------------------------------------------------------
import streamlit as st
import pickle
import pandas as pd
import requests
import time
import gdown
from dotenv import load_dotenv
import os

import base64

def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Load environment variables
load_dotenv()
api_key = os.getenv("TMDB_API_KEY")

# Safety check for missing API key
if not api_key:
    st.error("❌ TMDB API key is missing. Please set it in the .env file.")
    st.stop()

# ✅ Download .pkl files from Google Drive if not present
if not os.path.exists('movies.pkl'):
    gdown.download('https://drive.google.com/uc?id=1I9xLv98xEBRNL2vLZ07jFWM_9mKpcfAY', 'movies.pkl', quiet=False, fuzzy=True)

if not os.path.exists('similarity.pkl'):
    gdown.download('https://drive.google.com/uc?id=1K8rgJ0_SgkCeVmH4JlT-xeoTso_SFsJ8', 'similarity.pkl', quiet=False, fuzzy=True)

# Load data
with open('movies.pkl', 'rb') as f:
    movies_dict = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movies_dict)


# Fetch poster from TMDB
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        )
        data = response.json()
        if "poster_path" in data and data["poster_path"]:
            return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]
        else:
            return "https://via.placeholder.com/200x300?text=No+Poster"
    except:
        return "https://via.placeholder.com/200x300?text=Error"

# Fetch trailer from TMDB (YouTube)
def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"
        data = requests.get(url).json()
        for video in data.get("results", []):
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"
    except:
        pass
    return None

# Recommendation function
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    movie_names, posters, trailers = [], [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        trailers.append(fetch_trailer(movie_id))
    return movie_names, posters, trailers

# Streamlit Page Config
st.set_page_config(page_title="🎬 CineMate X - Movie Recommender", layout="wide")

# Add Custom Background Image & Overlay Styling
st.markdown("""
    <style>
        /* Background image for full app */
        .stApp {
            background:background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        /* Overlay for content readability */
        .main {
            background-color: rgba(0, 0, 0, 0.6);  /* transparent black overlay */
            padding: 2rem;
            border-radius: 12px;
        }

        /* Text & shadow */
        h1, p, label, .stSelectbox, .stButton {
            color: white !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        }
    </style>
""", unsafe_allow_html=True)

# Remove Streamlit Navbar and Footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Stylish Theme Toggle
st.markdown("""
    <style>
        .toggle-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .toggle-label {
            margin: 0 10px;
            font-weight: bold;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

theme = st.radio(
    "Select Theme",
    ["🌞 Light Mode", "🌚 Dark Mode"],
    horizontal=True,
    label_visibility="collapsed"
)

# Apply Custom Theme CSS
if theme == "🌚 Dark Mode":
    st.markdown("""
        <style>
            .stApp {
                background-color: #0f1117;
                color: #ffffff;
            }
            h1, p, label {
                color: #ffffff !important;
            }
            .stSelectbox > div {
                background-color: #1e1f26 !important;
                color: white !important;
            }
            .stButton>button {
                background-color: #2d2f3a !important;
                color: white !important;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: bold;
                transition: 0.3s;
            }
            .stButton>button:hover {
                background-color: #3a3c47 !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .stApp {
                background-color: #ffffff;
                color: #000000;
            }
            h1, p, label {
                color: #000000 !important;
            }
            .stButton>button {
                background-color: #f0f0f0 !important;
                color: black !important;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: bold;
                transition: 0.3s;
            }
            .stButton>button:hover {
                background-color: #3a3c47 !important;
            }
        </style>
    """, unsafe_allow_html=True)

# App Heading
st.markdown("<h1 style='text-align: center; color:#FF4B4B;'>🍿CineMate <span style='color:#00BFFF;'>X</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Choose your favorite movie and get 5 similar ones! 🎬</p>", unsafe_allow_html=True)

# Movie Selector
movie_list = movies["title"].values
movie_name = st.selectbox("🎥 Search and Select a Movie", movie_list)

if st.button("🍿 Recommend"):
    
    # Popcorn Loader
    st.markdown("""
        <style>
            .popcorn-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(0, 0, 0, 0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                flex-direction: column;
                animation: fadeOut 0.5s ease forwards;
                animation-delay: 2.4s;
            }
            .popcorn-box {
                width: 60px;
                height: 100px;
                background: linear-gradient(45deg, #e50914, #b81d24);
                border-radius: 8px 8px 4px 4px;
                position: relative;
                overflow: hidden;
            }
            .popcorn-kernel {
                width: 20px;
                height: 20px;
                background: #fffacd;
                border-radius: 50%;
                position: absolute;
                animation: pop 1.2s infinite ease-in-out;
            }
            .popcorn-kernel:nth-child(1) { top: 80%; left: 10%; animation-delay: 0s; }
            .popcorn-kernel:nth-child(2) { top: 80%; left: 40%; animation-delay: 0.3s; }
            .popcorn-kernel:nth-child(3) { top: 80%; left: 70%; animation-delay: 0.6s; }
            @keyframes pop {
                0% { transform: translateY(0); opacity: 1; }
                50% { transform: translateY(-60px); opacity: 0.6; }
                100% { transform: translateY(0); opacity: 1; }
            }
            .popcorn-text {
                color: white;
                font-size: 22px;
                margin-top: 20px;
                animation: blink 1.5s infinite;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.4; }
            }
            @keyframes fadeOut {
                to {
                    opacity: 0;
                    visibility: hidden;
                }
            }
        </style>

        <div class="popcorn-loader" id="loader">
            <div class="popcorn-box">
                <div class="popcorn-kernel"></div>
                <div class="popcorn-kernel"></div>
                <div class="popcorn-kernel"></div>
            </div>
            <div class="popcorn-text">Serving hot recommendations...</div>
        </div>
    """, unsafe_allow_html=True)

    time.sleep(0.1)

    # Show the searched movie
    searched_movie_id = movies[movies['title'] == movie_name].iloc[0].movie_id
    searched_poster = fetch_poster(searched_movie_id)

    st.markdown("## 🎬 Your Searched Movie", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='
            display: flex; 
            flex-direction: column; 
            align-items: left; 
            background: rgba(255,255,255,0.05); 
            padding: 20px; 
            border-radius: 16px; 
            box-shadow: 0px 4px 12px rgba(0,0,0,0.4); 
            margin-bottom: 30px;
        '>
            <img src="{searched_poster}" style='width: 200px; border-radius: 12px;' />
        </div>
    """, unsafe_allow_html=True)

    # Recommend movies
    names, posters, trailers = recommend(movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i])
            st.markdown(f"<div style='text-align: center; font-weight: bold;'>{names[i]}</div>", unsafe_allow_html=True)
            if trailers[i]:
                st.markdown(f"""
                    <div style='text-align: center; margin-top: 10px;'>
                        <a href="{trailers[i]}" target="_blank" style="
                            text-decoration: none;
                            padding: 8px 14px;
                            font-weight: 600;
                            color: white;
                            background: linear-gradient(135deg, #e50914, #b81d24);
                            border-radius: 10px;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
                        ">
                            ▶ Watch Trailer
                        </a>
                    </div> <br><br><br><br>
                """, unsafe_allow_html=True)
            else:
                st.caption("🚫 Trailer not available")


# Encode and embed images as base64
git_logo_base64 = get_base64_img("assets/gitlogo.png")
insta_logo_base64 = get_base64_img("assets/instalogo.png")

# Footer with clickable logos
st.markdown(f"""
    <style>
        .footer {{
            
        
            width: 100%;
            text-align: center;
            margin-top: 50px;
        }}
        .footer img {{
            margin: 0 10px;
            vertical-align: middle;
        }}
    </style>

    <div class="footer">
        <h4><i>Made with ❤️ by Sachin</i></h4>
       <p> <a href="https://github.com/Sachinsstac" target="_blank">
            <img src="data:image/png;base64,{git_logo_base64}" width="30" height="30" alt="GitHub">
        </a>|
        <a href="https://www.instagram.com/sachiiiiin.xx03" target="_blank">
            <img src="data:image/png;base64,{insta_logo_base64}" width="30" height="30" alt="Instagram">
        </a> </p>
    </div>
""", unsafe_allow_html=True)


# # Run the app with: streamlit run app.py