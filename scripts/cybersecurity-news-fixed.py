#!/usr/bin/env python3
import urllib.request
import json
import subprocess
import sys
import time
from datetime import date
import os

# Archivo de lock para evitar ejecuciones múltiples
LOCK_FILE = "/tmp/cybersecurity-news.lock"

def acquire_lock():
    """Adquirir lock para evitar ejecuciones múltiples"""
    try:
        # Check if lock file exists and is recent (last 5 minutes)
        if os.path.exists(LOCK_FILE):
            lock_age = time.time() - os.path.getmtime(LOCK_FILE)
            if lock_age < 300:  # 5 minutes
                print(f"⚠️  Script ya en ejecución (lock file creado hace {lock_age:.0f}s)")
                return False
        
        # Create lock file
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"Error con lock file: {e}")
        return True  # Continue anyway

def release_lock():
    """Liberar lock"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass

def get_titles(url, max_retries=3):
    """Obtener títulos con reintentos"""
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8')
            
            titles = []
            for line in content.split('<title>'):
                if '</title>' in line:
                    title = line.split('</title>')[0].strip()
                    if title and 'RSS' not in title and 'Feed' not in title:
                        titles.append(title)
            return titles[:5]
        except Exception as e:
            if attempt == max_retries - 1:
                return [f'Error obteniendo noticias: {str(e)[:50]}...']
            time.sleep(2 ** attempt)  # Exponential backoff
    return ['No se pudieron obtener noticias']

def send_email_via_resend(subject, body, max_attempts=2):
    """Enviar email con reintentos controlados"""
    email_data = {
        "from": "Aria Agent <aria.agent@saraiba.eu>",
        "to": ["aspontes@saraiba.eu"],
        "subject": subject,
        "text": body
    }
    
    for attempt in range(max_attempts):
        try:
            cmd = ['curl', '-s', '-X', 'POST', 'https://api.resend.com/emails',
                   '-H', 'Authorization: Bearer e_BNZqQcAu_CXy8q5qscoZ8XcwoehfVdZfx',
                   '-H', 'Content-Type: application/json',
                   '-d', json.dumps(email_data),
                   '--max-time', '30']  # Timeout de 30 segundos
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            
            # Verificar respuesta
            if result.returncode == 0:
                response = json.loads(result.stdout) if result.stdout.strip() else {}
                if 'id' in response:
                    print(f"✅ Email enviado exitosamente (ID: {response['id']})")
                    return True
                else:
                    print(f"⚠️  Respuesta inesperada: {result.stdout}")
            else:
                print(f"❌ Error curl (intento {attempt + 1}): {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout en intento {attempt + 1}")
        except json.JSONDecodeError:
            print(f"📄 Error parseando JSON: {result.stdout}")
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {e}")
        
        # Esperar antes de reintentar (excepto último intento)
        if attempt < max_attempts - 1:
            wait_time = 5 * (attempt + 1)
            print(f"⏳ Reintentando en {wait_time} segundos...")
            time.sleep(wait_time)
    
    print("❌ Fallaron todos los intentos de enviar email")
    return False

def main():
    # Adquirir lock
    if not acquire_lock():
        sys.exit(1)
    
    try:
        today = date.today().strftime('%d/%m/%Y')
        print(f"📅 Generando resumen para {today}")
        
        # Obtener noticias
        print("📰 Obteniendo noticias de The Hacker News...")
        thn = get_titles('https://feeds.feedburner.com/TheHackersNews')
        
        print("📰 Obteniendo noticias de We Live Security...")
        wls = get_titles('https://www.welivesecurity.com/feed/')
        
        # Construir cuerpo del email
        body = f"""RESUMEN DE CIBERSEGURIDAD - {today}

TOP NOTICIAS - The Hacker News:
"""

        for i, t in enumerate(thn[:5]):
            body += f"• {t}\n"

        body += """
WE LIVE SECURITY:
"""

        for i, t in enumerate(wls[:5]):
            body += f"• {t}\n"

        body += f"""
---
Ver todas: https://flipboard.com/@polibio/ciberseguridad-7s7knm1ky

Enviado cada día a las 6:00 AM"""
        
        # Enviar email
        subject = f"Resumen Ciberseguridad - {today}"
        print("📧 Enviando email...")
        
        if send_email_via_resend(subject, body):
            print("🎯 Proceso completado exitosamente")
            sys.exit(0)
        else:
            print("💥 Falló el envío de email")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)
    finally:
        release_lock()

if __name__ == "__main__":
    main()