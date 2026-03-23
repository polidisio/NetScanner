// Configuración de Notion - Versión corregida
// Usa API route de Vercel para acceder a variables de entorno

// Detect language
const userLang = navigator.language || navigator.userLanguage;
const isSpanish = userLang.startsWith('es');

const translations = {
    es: {
        loading: 'Cargando cita del día...',
        quoteOf: 'Cita del',
        saving: 'Guardando en Notion...',
        saved: 'Guardado en Notion ✓',
        error: 'Error al guardar',
        ready: 'Listo'
    },
    en: {
        loading: 'Loading quote of the day...',
        quoteOf: 'Quote of',
        saving: 'Saving to Notion...',
        saved: 'Saved to Notion ✓',
        error: 'Error saving',
        ready: 'Ready'
    }
};

const t = translations[isSpanish ? 'es' : 'en'];

// Citas famous
const fallbackQuotes = isSpanish ? [
    { text: "El conocimiento es poder.", author: "Francis Bacon" },
    { text: "Yo soy aquello que soy", author: "Popeye" },
    { text: "Que la fuerza te acompañe", author: "Yoda" },
    { text: "¡Elemental, querido Watson!", author: "Sherlock Holmes" },
    { text: "Hay algo en este barrio que no me gusta", author: "Batman" },
    { text: "Con gran poder viene gran responsabilidad", author: "Tío Ben" },
    { text: "Que el odds estén siempre a tu favor", author: "Han Solo" },
    { text: "Todo el mundo sospecha de alguien", author: "Agatha Christie" },
    { text: "No pienses, siente", author: "Bruce Lee" },
    { text: "Yo soy tu padre", author: "Darth Vader" },
    { text: "Después de todo, mañana es otro día", author: "Scarlett O'Hara" },
    { text: "La fuerza es fuerte en mi familia", author: "Luke Skywalker" },
    { text: "Volveré", author: "Terminator" },
    { text: "E.T. teléfono casa", author: "E.T." },
    { text: "Soy el rey del mundo", author: "Jack Dawson" },
    { text: "La vida es como una caja de bombones", author: "Forrest Gump" },
    { text: "Yo solo se que no se nada", author: "Sócrates" },
    { text: "Pienso luego existo", author: "Descartes" },
    { text: "Era inevitable", author: "Thanos" },
    { text: "Buena navegación", author: "Capitán Manthan" },
    { text: "Houston, tenemos un problema", author: "Apollo 13" },
    { text: "Bond. James Bond", author: "James Bond" },
    { text: "Era viernes", author: "El Mundo" },
    { text: "Que la suerte te acompañe", author: "Various" }
] : [
    { text: "Knowledge is power.", author: "Francis Bacon" },
    { text: "I am what I am", author: "Popeye" },
    { text: "May the Force be with you", author: "Yoda" },
    { text: "Elementary, my dear Watson", author: "Sherlock Holmes" },
    { text: "There's something wrong with this neighborhood", author: "Batman" },
    { text: "With great power comes great responsibility", author: "Uncle Ben" },
    { text: "May the odds be ever in your favor", author: "Han Solo" },
    { text: "Everyone suspects someone", author: "Agatha Christie" },
    { text: "Don't think, feel", author: "Bruce Lee" },
    { text: "I am your father", author: "Darth Vader" },
    { text: "After all, tomorrow is another day", author: "Scarlett O'Hara" },
    { text: "The Force is strong in my family", author: "Luke Skywalker" },
    { text: "I'll be back", author: "Terminator" },
    { text: "E.T. phone home", author: "E.T." },
    { text: "I'm the king of the world", author: "Jack Dawson" },
    { text: "Life is like a box of chocolates", author: "Forrest Gump" },
    { text: "I know nothing", author: "Socrates" },
    { text: "I think, therefore I am", author: "Descartes" },
    { text: "It was inevitable", author: "Thanos" },
    { text: "Houston, we have a problem", author: "Apollo 13" },
    { text: "Bond. James Bond", author: "James Bond" },
    { text: "It's Friday", author: "Friday" },
    { text: "May luck be with you", author: "Various" }
];

// Get current date
const today = new Date();

// Format date based on language
const dateStr = today.toLocaleDateString(isSpanish ? 'es-ES' : 'en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
});

// ISO date for API
const isoDate = today.toISOString().split('T')[0];

// Set current date in status bar
document.getElementById('currentDate').textContent = dateStr;

// Function to get daily quote based on date
function getDailyQuote() {
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    const index = dayOfYear % fallbackQuotes.length;
    return fallbackQuotes[index];
}

// Get both Spanish and English quotes
function getBothQuotes() {
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    
    const esQuotes = [
        { text: "El conocimiento es poder.", author: "Francis Bacon" },
        { text: "Yo soy aquello que soy", author: "Popeye" },
        { text: "Que la fuerza te acompañe", author: "Yoda" },
        { text: "¡Elemental, querido Watson!", author: "Sherlock Holmes" },
        { text: "Hay algo en este barrio que no me gusta", author: "Batman" },
        { text: "Con gran poder viene gran responsabilidad", author: "Tío Ben" },
        { text: "Que el odds estén siempre a tu favor", author: "Han Solo" },
        { text: "Todo el mundo sospecha de alguien", author: "Agatha Christie" },
        { text: "No pienses, siente", author: "Bruce Lee" },
        { text: "Yo soy tu padre", author: "Darth Vader" },
        { text: "Después de todo, mañana es otro día", author: "Scarlett O'Hara" },
        { text: "La fuerza es fuerte en mi familia", author: "Luke Skywalker" },
        { text: "Volveré", author: "Terminator" },
        { text: "E.T. teléfono casa", author: "E.T." },
        { text: "Soy el rey del mundo", author: "Jack Dawson" },
        { text: "La vida es como una caja de bombones", author: "Forrest Gump" },
        { text: "Yo solo se que no se nada", author: "Sócrates" },
        { text: "Pienso luego existo", author: "Descartes" },
        { text: "Era inevitable", author: "Thanos" },
        { text: "Buena navegación", author: "Capitán Manthan" },
        { text: "Houston, tenemos un problema", author: "Apollo 13" },
        { text: "Bond. James Bond", author: "James Bond" },
        { text: "Era viernes", author: "El Mundo" },
        { text: "Que la suerte te acompañe", author: "Various" }
    ];
    
    const enQuotes = [
        { text: "Knowledge is power.", author: "Francis Bacon" },
        { text: "I am what I am", author: "Popeye" },
        { text: "May the Force be with you", author: "Yoda" },
        { text: "Elementary, my dear Watson", author: "Sherlock Holmes" },
        { text: "There's something wrong with this neighborhood", author: "Batman" },
        { text: "With great power comes great responsibility", author: "Uncle Ben" },
        { text: "May the odds be ever in your favor", author: "Han Solo" },
        { text: "Everyone suspects someone", author: "Agatha Christie" },
        { text: "Don't think, feel", author: "Bruce Lee" },
        { text: "I am your father", author: "Darth Vader" },
        { text: "After all, tomorrow is another day", author: "Scarlett O'Hara" },
        { text: "The Force is strong in my family", author: "Luke Skywalker" },
        { text: "I'll be back", author: "Terminator" },
        { text: "E.T. phone home", author: "E.T." },
        { text: "I'm the king of the world", author: "Jack Dawson" },
        { text: "Life is like a box of chocolates", author: "Forrest Gump" },
        { text: "I know nothing", author: "Socrates" },
        { text: "I think, therefore I am", author: "Descartes" },
        { text: "It was inevitable", author: "Thanos" },
        { text: "Houston, we have a problem", author: "Apollo 13" },
        { text: "Bond. James Bond", author: "James Bond" },
        { text: "It's Friday", author: "Friday" },
        { text: "May luck be with you", author: "Various" }
    ];
    
    return {
        es: esQuotes[dayOfYear % esQuotes.length],
        en: enQuotes[dayOfYear % enQuotes.length]
    };
}

// Save to Notion via Vercel API route
async function saveToNotion() {
    try {
        const quotes = getBothQuotes();
        
        const response = await fetch('/api/save-quote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                quote_es: quotes.es.text,
                quote_en: quotes.en.text,
                author_es: quotes.es.author,
                author_en: quotes.en.author,
                date: isoDate
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            console.error('API error:', error);
            return { success: false, error: error.error || 'Unknown error' };
        }
        
        const data = await response.json();
        console.log('Saved to Notion:', data);
        return { success: true, data };
        
    } catch (error) {
        console.error('Save error:', error);
        return { success: false, error: error.message };
    }
}

// Check if already saved today (using localStorage)
function hasSavedToday() {
    const lastSaved = localStorage.getItem('quoteSavedDate');
    return lastSaved === isoDate;
}

// Mark as saved
function markAsSaved() {
    localStorage.setItem('quoteSavedDate', isoDate);
}

// Display the quote
const quote = getDailyQuote();

// Set loading text
document.getElementById('quote').textContent = t.loading;

// Load quote after a short delay
setTimeout(async () => {
    document.getElementById('quote').textContent = `"${quote.text}"`;
    document.getElementById('author').textContent = `— ${quote.author}`;
    document.getElementById('date').textContent = `${t.quoteOf} ${dateStr}`;
    document.getElementById('status').textContent = t.ready;
    
    // Auto-save to Notion if not saved today
    if (!hasSavedToday()) {
        document.getElementById('status').textContent = t.saving;
        
        const result = await saveToNotion();
        
        if (result.success) {
            markAsSaved();
            document.getElementById('status').textContent = t.saved;
        } else {
            document.getElementById('status').textContent = `${t.error}: ${result.error}`;
            // Keep trying? Or show manual save button?
        }
    }
}, 500);

// Optional: Add manual save button for debugging
function addManualSaveButton() {
    const button = document.createElement('button');
    button.textContent = '💾 Guardar manualmente';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 15px;
        background: #333;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'Roboto', sans-serif;
        z-index: 1000;
    `;
    button.onclick = async () => {
        button.disabled = true;
        button.textContent = 'Guardando...';
        
        const result = await saveToNotion();
        
        if (result.success) {
            button.textContent = '✅ Guardado';
            markAsSaved();
        } else {
            button.textContent = '❌ Error';
            alert(`Error: ${result.error}`);
        }
        
        setTimeout(() => {
            button.disabled = false;
            button.textContent = '💾 Guardar manualmente';
        }, 3000);
    };
    
    document.body.appendChild(button);
}

// Add button for debugging (optional)
// addManualSaveButton();