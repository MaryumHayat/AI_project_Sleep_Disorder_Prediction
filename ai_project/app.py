from flask import Flask, jsonify, render_template, request
import joblib
import numpy as np
from scipy.sparse import hstack

app = Flask(__name__) 

# Load components
model = joblib.load('model.pkl')
tfidf = joblib.load('tfidf.pkl')
target_le = joblib.load('target_encoder.pkl')
gender_le = joblib.load('gender_encoder.pkl')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    age = float(request.form['age'])
    gender = request.form['gender']
    user_input = request.form['description'].lower().strip()
    
    # Defaults
    ahi, oxygen = 15.0, 95.0 
    mapping_boost = ""
    keyword_found = False
    
    # 1. Insomnia (Covers difficulty falling asleep, staying asleep, waking up early, fatigue)
    if any(w in user_input for w in ["fall", "asleep", "awake", "insomnia", "tired", "difficulty", "frequently", "early"]):
        mapping_boost = " Insomnia difficulty falling staying asleep waking up early fatigue irritability"
        keyword_found = True

    # 2. Obstructive Sleep Apnea (Covers snoring, gasping, breathing)
    elif any(w in user_input for w in ["snore", "gasp", "apnea", "choke", "breath", "oxygen", "stop"]):
        ahi, oxygen = 40.0, 80.0
        mapping_boost = " Obstructive Sleep Apnea snoring gasping air pauses breathing apnea choking"
        keyword_found = True

    # 3. Parasomnias (Covers sleepwalking, nightmares, night terrors)
    elif any(w in user_input for w in ["walk", "nightmare", "terror", "dream", "act", "parasomnia"]):
        mapping_boost = " Parasomnias sleepwalking eating nightmares night terrors acting out dreams"
        keyword_found = True

    # 4. Restless Leg Syndrome (Covers leg movement, itching, crawling)
    elif any(w in user_input for w in ["leg", "crawl", "move", "itch", "kick", "discomfort"]):
        mapping_boost = " Restless Leg Syndrome urge move legs creepy crawly discomfort itching legs"
        keyword_found = True

    # 5. Narcolepsy (Covers daytime sleepiness, sudden urges)
    elif any(w in user_input for w in ["narcolepsy", "sudden", "urge", "sleepiness", "weakness", "cataplexy"]):
        mapping_boost = " Narcolepsy daytime sleepiness sudden sleep urge muscle weakness cataplexy"
        keyword_found = True

    # 6. Circadian Rhythm Disorder (Covers jet lag, shift work, body clock)
    elif any(w in user_input for w in ["jet lag", "shift", "work", "clock", "body", "alert", "cycle"]):
        mapping_boost = " Circadian Rhythm Disorder jet lag shift work body clock alert night sleepy day"
        keyword_found = True

    # 7. No Disorder (Covers feeling rested, healthy, normal sleep)
    elif any(w in user_input for w in ["well", "rested", "normal", "healthy", "good", "fine", "no issue"]):
        ahi, oxygen = 1.0, 99.0
        mapping_boost = " No Disorder sleep well rested normal no issues healthy sleep"
        keyword_found = True

    # --- AI PROCESSING ---
    
    # Combine original user input with our concentrated symptom words
    final_text = user_input + mapping_boost
    text_features = tfidf.transform([final_text])
    
    # Safety Check: If user types total gibberish
    if text_features.nnz == 0 and not keyword_found:
        return jsonify({"diagnosis": "Symptoms Not Clear"})

    gender_encoded = gender_le.transform([gender])[0]
    clinical_data = np.array([[age, gender_encoded, ahi, oxygen, 1]])
    final_input = hstack([clinical_data, text_features])
    
    # Prediction with dynamic threshold
    probs = model.predict_proba(final_input)[0]
    max_prob = np.max(probs)
    
    # If a keyword was matched, we are more confident (lower threshold)
    threshold = 0.25 if keyword_found else 0.45
    
    if max_prob < threshold:
        return jsonify({"diagnosis": "Symptoms Not Clear"})
    
    prediction_id = np.argmax(probs)
    result = target_le.inverse_transform([prediction_id])[0]

    return jsonify({"diagnosis": result})

if __name__ == "__main__":
    app.run(debug=True)