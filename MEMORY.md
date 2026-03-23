# MEMORY.md - Jose's Card Survivor Game

## Project Overview
Card Survivor is an iOS card game (Slay the Spire style) built with SwiftUI. Gothic/dark fantasy theme.

## Features Implemented
- 4 player classes (Warrior, Mage, Rogue, Paladin) with unique stats and progression
- 8 enemy types with intelligent AI
- Enemy intent system (visible attack/defense/buff/debuff)
- 35+ cards with rarities (common, uncommon, rare, epic, legendary)
- XP and leveling system
- Wave-based combat with shop
- Relic/progression system (persistent between games)
- Music system (MusicManager.swift)
- 8 gothic music tracks ready

## Art
- Generated basic pixel art placeholders
- User is generating better AI art via Perchance
- Images in OneDrive: "Image Game" folder need to be organized

## Technical
- Location: OneDrive Projects/CardSurvivor
- GitHub: github.com/polidisio/CardSurvivor
- Framework: SwiftUI

## Dashboard + Apple Notes Integration

- Dashboard local en http://localhost:5007/messages
- API: http://localhost:5007/api/messages
- Puedo guardar mensajes al dashboard via curl POST
- Puedo importar mensajes a Apple Notes via AppleScript
- Para importar: `osascript -e 'tell application "Notes" to tell account "iCloud" to make new note with properties {name:"Título", body:"Contenido"}'`

## Tareas Automáticas

- Evaluar mensajes de Telegram importantes y guardarlos automáticamente en dashboard + Apple Notes
- **Criterios de importancia:**
  - Comandos útiles, información nueva, decisiones
  - Proyectos, código, configuraciones
  - Listas, recomendaciones, cosas para recordar
  - NO: saludos, confirmaciones simples, off-topic
Jose wants gothic style. Working on generating proper game art via AI.
