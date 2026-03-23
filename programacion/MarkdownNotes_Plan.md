# MarkdownNotes - Plan de Desarrollo Completo

## 📝 Descripción del Proyecto

**Nombre:** MarkdownNotes  
**Tipo:** App iOS (SwiftUI)  
**Modelo de negocio:** Pago único ($4.99)  
**Enfoque:** Privacidad - datos locales + iCloud opcional, sin suscripción cloud  

---

## 🎯 Características

### MVP (v1.0)
- [x] Editor Markdown con TextEditor
- [x] Live Preview toggle
- [x] Crear/editar/borrar notas
- [x] Carpetas para organizar
- [x] Contador de palabras
- [x] Guardado automático local

### v1.1 - Exportación
- [ ] Exportar a PDF
- [ ] Exportar a HTML
- [ ] Exportar a DOCX (opcional)

### v1.2 - Mejoras Editor
- [ ] Syntax highlighting para código (Highlightr)
- [ ] Atajos de teclado para iPad
- [ ] Modo enfoque (ocultar UI)
- [ ] Buscar y reemplazar

### v2.0 - Sincronización
- [ ] iCloud sync opcional
- [ ] Historial de versiones local
- [ ] Backups automáticos

### v2.1 - Extras
- [ ] Templates (diario, novela, código)
- [ ] Estadísticas de escritura
- [ ] Temas (claro/oscuro)
- [ ] Etiquetas/tags

---

## Estructura del Proyecto

```
Markdown 🏗️Notes/
├── Sources/
│   ├── App/
│   │   └── MarkdownNotesApp.swift       ← Entry point
│   ├── Views/
│   │   ├── ContentView.swift            ← NavigationSplitView principal
│   │   ├── EditorView.swift             ← Editor con toolbar
│   │   ├── PreviewView.swift            ← Renderizado Markdown
│   │   ├── FolderListView.swift         ← Lista de carpetas
│   │   └── SettingsView.swift           ← Configuración
│   ├── Models/
│   │   ├── Note.swift                   ← Modelo nota
│   │   ├── Folder.swift                 ← Modelo carpeta
│   │   └── Tag.swift                    ← Modelo etiqueta
│   ├── ViewModels/
│   │   └── NotesViewModel.swift         ← Lógica de negocio
│   └── Utilities/
│       ├── MarkdownParser.swift         ← Utilidades Markdown
│       ├── ExportManager.swift          ← Exportación PDF/HTML
│       └── StorageManager.swift         ← Persistencia local
└── Resources/
    ├── Assets.xcassets/
    ├── Info.plist
    └── MarkdownNotes.entitlements
```

---

## 📦 Dependencias (SPM)

| Paquete | Versión | Uso |
|---------|---------|-----|
| Ink | 0.6.0+ | Parseo Markdown a HTML |
| Highlightr | 2.1.0+ | Syntax highlighting código |

---

## 💾 Persistencia

### Local (MVP)
- **Método:** JSON + FileManager
- **Ubicación:** `Documents/notes/`
- **Formato:** Un archivo JSON por nota

### iCloud (v2.0)
- **Método:** NSUbiquitousKeyValueStore o CloudKit
- **Sync:** Automático via iCloud Drive

---

## 📤 Exportación

### PDF
```swift
// Usar UIGraphicsPDFRenderer o Native PDFKit
```

### HTML
```swift
// Ink.parse() → HTML string
```

---

## ⏱️ Estimación de Tiempo

| Fase | Tiempo |
|------|--------|
| MVP | 2-3 semanas |
| v1.1 Exportación | 1 semana |
| v1.2 Editor | 1-2 semanas |
| v2.0 iCloud | 2 semanas |
| v2.1 Extras | 1 semana |
| **Total** | **~2 meses** |

---

## 🔧 Comandos Útiles

```bash
# Generar proyecto
cd ~/OneDrive/Documents/MarkdownNotes
xcodegen generate

# Abrir en Xcode
open MarkdownNotes.xcodeproj
```

---

## 📱 Requisitos

- **iOS:** 16.0+
- **Dispositivos:** iPhone, iPad
- **Apple Developer:** Necesario para iCloud (opcional)

---

## 📋 Checklist de Desarrollo

- [x] Crear proyecto XcodeGen
- [x] NavigationSplitView básica
- [x] EditorView con TextEditor
- [x] PreviewView con parsing
- [x] Modelos Note y Folder
- [ ] StorageManager (persistencia)
- [ ] ExportManager (PDF/HTML)
- [ ] Highlightr integration
- [ ] iCloud sync
- [ ] Tests unitarios
- [ ] App Store preparation

---

*Creado: 2026-03-09*  
*Última actualización: 2026-03-09*
