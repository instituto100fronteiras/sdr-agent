
from flask import Flask, request, jsonify, abort
from config.settings import WEBHOOK_SECRET, WEBHOOK_PORT
from services.message_service import message_service
from services.lead_service import lead_service
from utils.logger import logger
from utils.validators import normalize_phone

app = Flask(__name__)

def validate_secret(f):
    """Decorator para validar o segredo no header (segurança básica)."""
    def wrapper(*args, **kwargs):
        # Se WEBHOOK_SECRET não estiver definido, assume que não precisa de auth (dev mode)
        # Se estiver, verifica o header 'X-Webhook-Secret' ou similar
        if WEBHOOK_SECRET:
            secret = request.headers.get("X-Webhook-Secret")
            if secret != WEBHOOK_SECRET:
                logger.warning("Tentativa de acesso ao webhook com segredo inválido.")
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/webhook/evolution", methods=["POST"])
@validate_secret
def webhook_evolution():
    """
    Recebe eventos da Evolution API (mensagens recebidas).
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "ignored", "reason": "no data"}), 200

        # Identifica tipo de evento (Evolution pode mandar vários tipos)
        event_type = data.get("type")
        
        # Foca apenas em mensagens de texto recebidas (MESSAGE_UPSERT ou similar)
        # Estrutura típica Evolution v1/v2
        message_data = data.get("data", {})
        key = message_data.get("key", {})
        from_me = key.get("fromMe", False)
        
        if from_me:
             # Ignora mensagens enviadas por nós mesmos (sync)
             return jsonify({"status": "ignored", "reason": "from_me"}), 200
        
        # Extrai telefone e conteúdo
        remote_jid = key.get("remoteJid", "") # ex: 554599998888@s.whatsapp.net
        phone = remote_jid.split("@")[0]
        
        message_content = message_data.get("message", {})
        text = message_content.get("conversation") or \
               message_content.get("extendedTextMessage", {}).get("text")
               
        if not text:
            logger.debug("Webhook recebido sem texto (imagem, áudio, etc). Ignorando por enquanto.")
            return jsonify({"status": "ignored", "reason": "no text"}), 200

        logger.info(f"Webhook Evolution recebido de {phone}: {text[:50]}...")
        
        # Processa a mensagem
        message_service.handle_incoming(normalize_phone(phone), text)
        
        return jsonify({"status": "processed"}), 200

    except Exception as e:
        logger.error(f"Erro no webhook evolution: {e}")
        return jsonify({"error": "Internal Error"}), 500

@app.route("/webhook/chatwoot", methods=["POST"])
# @validate_secret # Chatwoot nem sempre envia headers customizados facilmente configuráveis, manter opcional
def webhook_chatwoot():
    """
    Recebe eventos do Chatwoot (mudança de status, interação manual).
    """
    try:
        data = request.json
        event = data.get("event")
        
        if event == "conversation_status_changed":
            # Ex: Agente manual fechou a conversa ou marcou como resolvida
            meta = data.get("meta", {})
            sender = meta.get("sender", {})
            
            # Se for uma ação manual (user), podemos querer atualizar algo no nosso banco
            # Por enquanto, apenas logamos
            contact = data.get("meta", {}).get("sender", {})
            phone = contact.get("phone_number", "")
            status = data.get("status") # 'resolved', 'open', etc
            
            logger.info(f"Evento Chatwoot: status da conversa com {phone} mudou para {status}")
            
            # TODO: Se humano resolver, mover lead para status 'converted' ou 'finished'?
            # Deixar para Fase 2 por segurança.
            
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook chatwoot: {e}")
        return jsonify({"error": "Internal Error"}), 500

def start_server():
    logger.info(f"Iniciando servidor de Webhooks na porta {WEBHOOK_PORT}...")
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    start_server()
