import requests

def send_whatsapp_message(phone_number: str, message: str, phone_number_id: str, access_token: str, use_template: bool = False, template_name: str = "hello_world", template_lang: str = "en_US"):
    """
    Envia uma mensagem via API oficial do WhatsApp Business (Meta/Facebook).
    - phone_number: número de destino no formato E.164 (ex: 15551634902)
    - message: texto da mensagem (ignorado se use_template=True)
    - phone_number_id: ID do número de telefone do painel do Facebook Developers
    - access_token: token de acesso da API do Facebook/Meta
    - use_template: se True, envia mensagem de template (ex: hello_world)
    - template_name: nome do template aprovado (default: hello_world)
    - template_lang: código do idioma do template (default: en_US)
    """
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    if use_template:
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_lang}
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[WHATSAPP] Erro ao enviar mensagem: {e}")
        return None
