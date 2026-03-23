# NewsBot 🤖

Telegram bot personal para recibir resúmenes de noticias según tus intereses.

## Temas soportados

- 🚴 Ciclismo / Zwift
- 🤖 IA / LLM
- 📱 iOS Dev
- 🎮 Gaming
- 📰 Noticias generales

## Setup

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export TELEGRAM_BOT_TOKEN="tu-token"
export MINIMAX_API_KEY="tu-api-key"

# Ejecutar
python -m src.bot
```

## Comandos

- `/start` - Iniciar el bot
- `/subscribe <tema>` - Suscribirse a un tema
- `/unsubscribe <tema>` - Desuscribirse
- `/list` - Ver suscripciones
- `/news` - Recibir noticias ahora
- `/help` - Ayuda

## Desarrollo

```bash
# Tests
pytest tests/ -v

# Run
python -m src.bot
```

## Estructura

```
NewsBot/
├── src/
│   ├── __init__.py
│   ├── bot.py          # Main bot
│   ├── news_fetcher.py # Fetch news
│   ├── summarizer.py   # LLM summarization
│   └── config.py       # Configuration
├── tests/
├── docs/
└── requirements.txt
```

## Licencia

MIT
