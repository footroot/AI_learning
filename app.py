import os
import re
import ollama
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so your local HTML webpage can safely talk to this backend
CORS(app)

MODEL_NAME = "llama3.2"

def load_documents():
    documents = []
    files = ["security.txt", "rental.txt"]
    for file in files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                # Split text by paragraphs to make chunks
                chunks = [p.strip() for p in f.read().split("\n\n") if p.strip()]
                documents.extend(chunks)
    return documents

def find_most_relevant_context(user_query, docs):
    query_words = set(re.findall(r'\w+', user_query.lower()))
    best_match_idx = 0
    highest_score = -1
    
    for idx, doc in enumerate(docs):
        doc_words = set(re.findall(r'\w+', doc.lower()))
        matching_words = query_words.intersection(doc_words)
        score = len(matching_words)
        
        if score > highest_score:
            highest_score = score
            best_match_idx = idx
            
    return docs[best_match_idx] if docs else ""

# Define the web API endpoint that your JavaScript fetches
@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.get_json()
    user_question = data.get("question", "")
    
    if not user_question:
        return jsonify({"answer": "Please ask a valid question."}), 400
    
    # 1. Dynamically reload text files in case you update them
    documents = load_documents()
    if not documents:
        return jsonify({"answer": "Error: Local knowledge base files are empty."}), 500
        
    # 2. Match keywords
    matched_context = find_most_relevant_context(user_question, documents)
    
    # 3. Construct prompt for Ollama
    system_prompt = (
        f"You are a helpful assistant for the website mytaller.info.\n"
        f"Answer the user's question using ONLY this context: {matched_context}\n"
        f"If the answer isn't in the context, say you don't know."
    )
    
    try:
        # 4. Generate local response
        ai_response = ollama.generate(
            model=MODEL_NAME,
            system=system_prompt,
            prompt=user_question
        )
        return jsonify({"answer": ai_response['response']})
        
    except Exception as e:
        return jsonify({"answer": f"Error running local model: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting mytaller.info local AI backend on http://127.0.0.1:5000 ...")
    app.run(port=5000, debug=True)
