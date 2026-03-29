from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# 1. SETUP: Replace with your actual API Key
client = genai.Client(api_key="AIzaSyDD342StTylXfG_olzb98cl9IsLCgyclME")

# 2. THE "BRAIN" UPDATE: 
# This tells Gemini exactly how to behave. 
# We added "Be very brief" and "Avoid long paragraphs" to fix the 'big answers' issue.
# Update this part in your app.py
instruction = (
    "You are a knowledgeable Ocean and Climate Scientist. "
    
    "1. Always start with a direct lead-in sentence that rephrases the user's question "
    "(e.g., 'The process of ocean acidification happens because...'). "
    
    "2. For theory or 'how-to' questions, explain using 2-3 clear sentences in a paragraph. "
    
    "3. Use bullet points ONLY when the user asks for a list of specific items, "
    "names, or types (like 'fishes', 'oceans', or 'causes'). "
    
    "4. Keep the overall tone professional and scientific but easy to understand."
)

# Initialize the chat session with the instructions
chat = client.chats.create(
    model='gemini-2.5-flash',
    config={'system_instruction': instruction}
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    # This receives the message from your HTML 'fetch' call
    user_input = request.json.get("message")
    try:
        # Send the message to Gemini
        response = chat.send_message(user_input)
        
        # Return the answer back to the HTML
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Default Flask port is 5000
    app.run(debug=True, port=5000)