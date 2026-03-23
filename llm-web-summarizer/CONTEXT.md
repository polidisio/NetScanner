# LLM Web Summarizer - Proyecto Contexto

## 📋 Descripción
Scraper web que usa LLM (MiniMax) para extraer y resumir contenido de URLs automáticamente.

## 🚀 Inicio Rápido

```bash
# 1. Clonar
git clone https://github.com/polidisio/llm-web-summarizer.git
cd llm-web-summarizer

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar API key
export MINIMAX_API_KEY="tu-api-key"

# 4. Usar
python3 main.py "https://ejemplo.com"
```

## 📁 Estructura

```
llm-web-summarizer/
├── main.py          # CLI entry point
├── scraper.py       # Web scraping (BeautifulSoup)
├── llm.py           # Integración LLM (MiniMax, OpenAI)
├── config.py        # Config loader
├── config.yaml      # Configuración
├── requirements.txt # Dependencias
├── test_scraper.py # Tests unitarios
└── README.md
```

## 🔧 Configuración

### Variables de entorno
```bash
export MINIMAX_API_KEY="tu-minimax-api-key"
export OPENAI_API_KEY="tu-openai-api-key"  # opcional
```

### config.yaml
```yaml
default_provider: minimax
minimax:
  api_key: "tu-api-key"
  base_url: "https://api.minimax.chat/v1"
  default_model: "MiniMax-M2.5"

scraper:
  timeout: 30
  max_retries: 3
```

## 💻 Uso CLI

```bash
# Basic
python3 main.py "https://ejemplo.com"

# Solo scraping (sin LLM)
python3 main.py "https://ejemplo.com" --no-summarize

# Con OpenAI
python3 main.py "https://ejemplo.com" --provider openai --model gpt-4o

# Verbose
python3 main.py "https://ejemplo.com" -v
```

## 🔌 Uso como Librería

```python
from scraper import scrape_url
from llm import summarize_with_llm

# Extraer contenido
data = scrape_url("https://ejemplo.com")
print(data["title"])
print(data["content"])

# Resumir con LLM
summary = summarize_with_llm(
    text=data["content"],
    provider="minimax",
    max_length=300
)
print(summary)
```

## 🧪 Tests

```bash
# Instalar pytest
pip install pytest

# Ejecutar tests
python3 -m pytest test_scraper.py -v
```

## 📊 Modelos Soportados

| Provider | Modelos |
|----------|---------|
| MiniMax | MiniMax-M2.5, M2.7 |
| OpenAI | gpt-4o, gpt-4o-mini |

## 🔗 Enlaces Útiles

- **Repo:** https://github.com/polidisio/llm-web-summarizer
- **MiniMax API:** https://platform.minimax.io
- **MiniMax Coding Plan:** https://platform.minimax.io/subscribe/coding-plan

## 📝 Notas

- Requiere Python 3.9+
- Usa BeautifulSoup + lxml para scraping
- Soporta MiniMax Coding Plan (gratis para coding)
- La API de MiniMax estándar NO funciona con Coding Plan keys

## 🚧 Posibles Mejoras

- [ ] Soporte para más providers (Anthropic, Google)
- [ ] Guardado en cache de scrapeos
- [ ] Modo daemon para monitoreo continuo
- [ ] API REST con FastAPI
- [ ] Interfaz web
- [ ] Integración con Telegram para alerts
- [ ] Tests para módulo LLM

## 👥 Creditos

Creado: 19/03/2026
Autor: Jose + Aria (OpenClaw)
