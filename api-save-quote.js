// api/save-quote.js - Vercel Serverless Function
export default async function handler(req, res) {
    // Solo permitir POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    
    try {
        const { quote_es, quote_en, author_es, author_en, date } = req.body;
        
        // Validar datos requeridos
        if (!quote_es || !quote_en || !date) {
            return res.status(400).json({ error: 'Missing required fields' });
        }
        
        // Obtener variables de entorno
        const NOTION_API_KEY = process.env.NOTION_API_KEY;
        const NOTION_PAGE_ID = process.env.NOTION_PAGE_ID;
        
        if (!NOTION_API_KEY || !NOTION_PAGE_ID) {
            console.error('Notion environment variables not configured');
            return res.status(500).json({ error: 'Server configuration error' });
        }
        
        // Crear página en Notion
        const response = await fetch('https://api.notion.com/v1/pages', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${NOTION_API_KEY}`,
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                parent: { page_id: NOTION_PAGE_ID },
                properties: {
                    title: [
                        {
                            text: {
                                content: `${quote_es} — ${author_es || 'Unknown'}`
                            }
                        }
                    ],
                    // Propiedades adicionales para filtrado
                    Date: {
                        date: {
                            start: date
                        }
                    },
                    Language: {
                        select: {
                            name: 'Bilingual'
                        }
                    }
                },
                children: [
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [
                                {
                                    text: {
                                        content: `📅 ${date}`
                                    }
                                }
                            ]
                        }
                    },
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [
                                {
                                    text: {
                                        content: `🇪🇸 "${quote_es}"`
                                    }
                                }
                            ]
                        }
                    },
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [
                                {
                                    text: {
                                        content: `👤 ${author_es || 'Unknown'}`
                                    }
                                }
                            ]
                        }
                    },
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [
                                {
                                    text: {
                                        content: `🇬🇧 "${quote_en}"`
                                    }
                                }
                            ]
                        }
                    },
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [
                                {
                                    text: {
                                        content: `👤 ${author_en || 'Unknown'}`
                                    }
                                }
                            ]
                        }
                    }
                ]
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Notion API error:', errorText);
            return res.status(500).json({ 
                error: 'Failed to save to Notion',
                details: errorText 
            });
        }
        
        const data = await response.json();
        
        return res.status(200).json({
            success: true,
            notionPageId: data.id,
            url: data.url
        });
        
    } catch (error) {
        console.error('Server error:', error);
        return res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
}