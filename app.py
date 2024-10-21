import streamlit as st
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile
import requests
from streamlit_lottie import st_lottie
import json


# Lottie animation function
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Load Google-themed Lottie animation (verified URL)
lottie_google_fact_check = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_t9gkkhz4.json")

# Page configuration
st.set_page_config(page_title="Asclepius AI", page_icon="🔍", layout="wide")

# Set custom CSS for Google theme colors
st.markdown("""
    <style>
    .reportview-container {
        background: #ffffff;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #4285F4, #34A853, #FBBC05, #EA4335);
    }
    .stTextInput > div > input {
        border: 2px solid #4285F4;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4285F4;
        color: white;
        border-radius: 12px;
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Title with Google colors
st.title("🔍 Asclepius AI")

# Add some space with animation
if lottie_google_fact_check:
    st_lottie(lottie_google_fact_check, height=250, key="google_fact_check")
else:
    st.error("Failed to load animation. Please check the URL.")

st.markdown(
    """
    <div style="text-align: center;">
    <h2 style="color: #4285F4; font-size: 40px;">Your AI Health Companion! The Future of Personalized Care</h2>
    <p style="font-size: 20px;">Powered by AI Hackathon and Devpost</p>
    </div>
    """, unsafe_allow_html=True
)

sample_prompt = """You are a medical practictioner and an expert in analyzing medical-related images working for a very reputed hospital. 
You will be provided with images and you need to identify the anomalies, any disease or health issues. 
You need to generate the result in a detailed manner. Write all the findings, next steps, recommendation, etc. 
You only need to respond if the image is related to a human body and health issues. You must have to answer but also write a disclaimer saying that "Consult with a Doctor before making any decisions".
Remember, if certain aspects are not clear from the image, it's okay to state 'Unable to determine based on the provided image.'

Now analyze the image and answer the above questions in the same structured manner defined above."""

# Sidebar explaining the healthcare chatbot
st.sidebar.title("About Asclepius AI")
st.sidebar.markdown("""
Asclepius AI is an intelligent healthcare chatbot designed to assist users with medical image analysis. 
The chatbot utilizes advanced AI models to analyze medical images and provide detailed findings, recommendations, and next steps. 
Its purpose is to help healthcare professionals and individuals in understanding complex medical data, while offering insights into potential health issues. 
Please note, the results are not a substitute for professional medical advice, and we always recommend consulting with a healthcare provider.
### Key Features:
- **Image Analysis**: Upload medical images for AI-powered analysis.
- **Simplified Explanation**: Get complex medical data explained in simpler terms, perfect for non-experts.
- **24/7 Accessibility**: Available anytime to assist with medical inquiries.
- **Ethical Disclaimer**: Always consult with a doctor before making health-related decisions.
""")

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'result' not in st.session_state:
    st.session_state.result = None

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4_model_for_analysis(filename: str, sample_prompt=sample_prompt):
    base64_image = encode_image(filename)
    
    messages = [
        {
            "role": "user",
            "content":[
                {
                    "type": "text", "text": sample_prompt
                    },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                        }
                    }
                ]
            }
        ]

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = messages,
        max_tokens = 1500
        )

    print(response.choices[0].message.content)
    return response.choices[0].message.content


def chat_student(query):
    chat_student_prompt = "You have to explain the below piece of information to a five years old. \n" + query
    messages = [
        {
            "role": "user",
            "content": chat_student_prompt
        }
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1500
    )

    return response.choices[0].message.content

st.title("Personalized HealthCare Chatbot")

with st.expander("About this App"):
    st.write("Multimodal Analysis: The chatbot correlates findings from uploaded images, enhancing diagnostic accuracy")
    st.write("Voice Activation: Users can interact with chatbot using voice commands, making it easier to access")
    st.write("Data Encryption: Ensure that all user data, including images and personal information, is encrypted")

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# Temporary file handling
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name

    st.image(uploaded_file, caption='Uploaded Image')

# Process button
if st.button('Analyze Image'):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        st.session_state['result'] = call_gpt4_model_for_analysis(st.session_state['filename'])
        st.markdown(st.session_state['result'], unsafe_allow_html=True)
        os.unlink(st.session_state['filename'])  # Delete the temp file after processing

# Chat for Children Explanation
if 'result' in st.session_state and st.session_state['result']:
    st.info("Below you have an option to understand in simpler terms.")
    if st.radio("Explain in Layman Terms", ('No', 'Yes')) == 'Yes':
        simplified_explanation = chat_student(st.session_state['result'])
        st.markdown(simplified_explanation, unsafe_allow_html=True)
