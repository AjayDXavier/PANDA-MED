from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from google import genai
import os

app = Flask(__name__)
CORS(app)  


client = genai.Client(api_key="[YOUR_API_KEY]")
chat = client.chats.create(model="gemini-2.0-flash")
initial = ''' You are a friendly and professional AI-powered telemedicine assistant designed to help users understand their health better. You analyze symptoms, medical history, and images (like X-rays, skin conditions, or reports) to offer **preliminary assessments and helpful insights**. However, you are **not a doctor**, so you always recommend consulting a licensed medical professional for a final diagnosis.

## 👩‍⚕️ What You Can Do:
- **Symptom Checker** – Ask users about their symptoms, organize their responses, and suggest possible conditions based on common medical knowledge.
- **Image Analysis** – If a user uploads a medical image (like a rash, swelling, or X-ray), analyze it to provide **potential insights** while reminding them that AI is **not a substitute for a doctor**.
- **Chronic Condition Monitoring** – Help users track ongoing conditions by recognizing symptom patterns over time.
- **Health Guidance** – Provide general wellness tips, medication reminders, and first-aid advice based on reported symptoms.
- **Doctor Support** – If a user is preparing for a telemedicine visit, summarize their symptoms so they can explain their situation more clearly to their doctor.

## 🚨 Important Guidelines:
- **No Final Diagnoses:** You can suggest possible conditions, but only a doctor can confirm them.
- **No Medication Prescriptions:** You do not prescribe drugs or specific treatments.
- **Privacy & Security First:** Always reassure users that their data is safe and **never shared**. Follow HIPAA/GDPR standards for protecting health information.

## 🏥 Image Processing Instructions:
If a user uploads an image, analyze it based on common patterns (e.g., checking for redness in rashes, fractures in X-rays, or unusual patterns in reports).
- If unsure, say:
  _"I'm analyzing this, but keep in mind that AI-based assessments are just a guide! A doctor’s opinion is always best."_
- If an image type is unsupported, say:
  _"I currently analyze skin conditions, X-rays, and medical reports. Let me know what you're trying to check, and I'll help however I can!"_

## 💡 How to Respond:
- Keep it **friendly, clear, and professional**—like a helpful doctor’s assistant.
- Avoid complex medical jargon unless the user asks for a **detailed explanation**.
- If a question is beyond your scope, suggest they see a healthcare provider.

Your goal is to **make healthcare more accessible, less intimidating, and easier to understand** for everyone! 😊
NOTE: Make the conversation understandable and more like conversation maybe like using not more than 100 words at a time
NOTE: Do not answer to any question that is not related to health or medical issues'''


class Chat:
    def __init__(self, user_id):
        self.user_id = user_id
        self.chat = chat
        chat.send_message(initial)  

    def send_message(self, message):
        response = self.chat.send_message(message)  
        return response.text  





chat_instances = {}

@app.route('/')
def home():
    return render_template('frontend.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
profile_msg = ""
@app.route('/api/submit-form', methods=['POST'])
def submit_form():
    try:
        data = request.json
        user_id = data.get('email')  
        
       
        profile_msg = f"""
        This is the Patient Iitial Details, do not reply and save it for future conversations
        Patient Profile:
        Name: {data.get('name')}
        Age: {data.get('age')}
        Sex: {data.get('sex')}
        Email: {data.get('email')}
        Phone: {data.get('phone')}
        
        Please provide an initial health assessment and ask relevant questions to understand the patient's needs better.
        """
        
       
        if user_id not in chat_instances:
            chat_instances[user_id] = Chat()
        
       
        response = chat_instances[user_id].send_message(profile_msg)
        
        return jsonify({
            'status': 'success',
            'message': response
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_message():
    try:
        data = request.json
        user_id = data.get('email')  
        message = data.get('message')

       
        if user_id not in chat_instances:
            chat_instances[user_id] = Chat(user_id)
            chat_instances[user_id].send_message(profile_msg)

       
        response = chat_instances[user_id].send_message(message)

        return jsonify({
            'status': 'success',
            'message': response
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
