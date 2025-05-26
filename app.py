from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DO BACKEND GEMINI ---
load_dotenv() # Carrega variáveis do arquivo .env
API_KEY = os.getenv("GOOGLE_API_KEY")

GEMINI_INITIALIZED = False
gemini_model = None

if not API_KEY:
    print("Erro CRÍTICO: Chave de API GOOGLE_API_KEY não encontrada no arquivo .env.")
else:
    try:
        genai.configure(api_key=API_KEY)
        print("INFO: API Key do Gemini configurada com sucesso.")
        MODEL_NAME = "models/gemini-1.5-flash-latest" # Ou seu modelo preferido
        # Configurações de geração (copie do seu código anterior)
        generation_config = { "temperature": 0.7, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192, "response_mime_type": "text/plain" }
        safety_settings = [ {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"} ]
        SYSTEM_INSTRUCTION = """Você é Valerium, um assistente de IA altamente especializado e dedicado exclusivamente a responder perguntas sobre história. Sua base de conhecimento é vasta em eventos históricos, figuras importantes, períodos, culturas e conceitos históricos globais. Seu objetivo é fornecer respostas precisas, informativas e contextualmente ricas, como Valerium, o guardião do conhecimento histórico. Se uma pergunta não estiver claramente relacionada à história (eventos passados, figuras históricas, arqueologia, historiografia, etc.), você deve educadamente informar ao usuário que sua especialização, como Valerium, é estritamente história e que não pode responder sobre outros tópicos. Não invente informações. Se você, Valerium, não tiver certeza sobre uma resposta ou não tiver informações suficientes sobre um tópico histórico muito específico ou obscuro, declare isso honestamente em vez de especular. Mantenha um tom formal, erudito e educativo, digno de Valerium. Priorize a precisão e a profundidade factual nas suas respostas."""

        gemini_model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=SYSTEM_INSTRUCTION
        )
        print(f"INFO: Modelo Gemini '{MODEL_NAME}' para Valerium inicializado com sucesso.")
        GEMINI_INITIALIZED = True
    except Exception as e:
        print(f"Erro CRÍTICO ao configurar ou inicializar o modelo Gemini: {e}")

# --- FIM DA CONFIGURAÇÃO DO GEMINI ---


app = Flask(__name__)

@app.route('/')
def index():
    """Serve a página principal do chat."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    """Recebe mensagens do usuário e retorna a resposta da IA."""
    if not GEMINI_INITIALIZED or gemini_model is None:
        return jsonify({"error": "Valerium não está disponível no momento (modelo não inicializado)."}), 503

    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message or not user_message.strip():
            return jsonify({"error": "Nenhuma mensagem recebida."}), 400

        print(f"Backend recebeu: {user_message}")

        # Chama a API Gemini
        response = gemini_model.generate_content(user_message)
        
        ia_reply = "Valerium não conseguiu processar sua solicitação." # Fallback
        if response and hasattr(response, 'parts') and response.parts and hasattr(response, 'text') and response.text:
            ia_reply = response.text
        elif response and hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
            ia_reply = f"Valerium não pôde responder: {response.prompt_feedback.block_reason}"
        
        print(f"Valerium respondeu: {ia_reply}")
        return jsonify({"reply": ia_reply})

    except Exception as e:
        print(f"Erro no endpoint /chat: {e}")
        return jsonify({"error": f"Ocorreu um erro interno em Valerium: {e}"}), 500

if __name__ == '__main__':
    # Isso é útil para rodar localmente com `python app.py`
    # Mas em produção (Render), Gunicorn será usado.
    # O Render vai setar a porta automaticamente.
    # Você pode remover essa parte ou mantê-la para testes locais.
    port = int(os.environ.get("PORT", 5000)) # Porta padrão 5000 se PORT não estiver setado
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False em produção