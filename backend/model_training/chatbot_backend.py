from flask import Flask, request, jsonify
from llama_cpp import Llama

model_path = "E:/Shwasnetra/backend/model_training/mythomax-l2-13b.Q4_0.gguf"
llm = Llama(model_path=model_path)

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    output = llm(question, max_tokens=128)
    return jsonify({"reply": output['choices'][0]['text'].strip()})

if __name__ == "__main__":
    app.run(port=5100, debug=True)
