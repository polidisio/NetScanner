# Card Survivor - Specification

## 1. Project Overview

- **Name**: Card Survivor
- **Genre**: Card-based survival game
- **Core Functionality**: A roguelike card game where players use cards to defeat waves of enemies and survive as long as possible
- **Target Users**: Casual mobile gamers who enjoy strategy and card games

## 2. Game Mechanics

### Core Loop
1. Player draws 3-5 cards per turn
2. Player plays cards to attack/defend
3. Enemies attack player
4. Repeat until player dies or clears wave
5. Between waves: shop to buy new cards

### Card Types
- **Attack Cards**: Deal damage to enemies
- **Defense Cards**: Block incoming damage  
- **Power Cards**: Buffs/debuffs (extra damage, healing, etc.)

### Enemy Types
- **Basic**: Weak, single target
- **Fast**: Low HP, attacks twice
- **Tank**: High HP, slow attacks
- **Boss**: Appears every 5 waves

### Progression
- **Score**: Based on enemies defeated + waves survived
- **Gold**: Earned from enemies, spent in shop
- **New Cards**: Unlocked through gameplay

## 3. Technical Specification

### Technology
- **Framework**: SwiftUI + SpriteKit
- **Language**: Swift 5.9+
- **Min iOS**: iOS 16.0
- **Architecture**: MVVM

### Project Structure
```
CardSurvivor/
├── App/
│   └── CardSurvivorApp.swift
├── Models/
│   ├── Card.swift
│   ├── Enemy.swift
│   ├── Player.swift
│   └── GameState.swift
├── Views/
│   ├── GameView.swift
│   ├── CardView.swift
│   ├── EnemyView.swift
│   └── ShopView.swift
├── ViewModels/
│   └── GameViewModel.swift
├── Services/
│   ├── CardManager.swift
│   └── GameEngine.swift
├── Resources/
│   └── Assets.xcassets
└── Info.plist
```

### Data Storage
- **UserDefaults**: High scores, settings
- **JSON Files**: Card definitions, enemy definitions

## 4. UI/UX Design

### Visual Style
- **Theme**: Dark fantasy with vibrant card colors
- **Cards**: Rounded rectangles with icons and stats
- **Enemies**: Simple 2D sprites (can be SF Symbols initially)
- **Animations**: Smooth card transitions, attack effects

### Color Palette
- **Background**: Dark gray (#1C1C1E)
- **Primary**: Purple (#BF5AF2) - for power cards
- **Attack**: Red (#FF453A) - for damage cards
- **Defense**: Blue (#0A84FF) - for shield cards
- **Gold**: Yellow (#FFD60A) - for currency
- **Text**: White (#FFFFFF)

### Screen Layout
1. **Main Menu**: Play button, High Scores, Settings
2. **Game Screen**: 
   - Top: Wave number, Score, Gold
   - Center: Enemy area
   - Bottom: Player HP, Hand of cards
3. **Shop Screen**: Grid of cards to buy
4. **Game Over**: Score, Play Again, Menu

## 5. Monetization

### Option A: Free + Ads
- Ad after each wave (optional)
- Reward ad for extra gold

### Option B: Premium ($0.99)
- No ads
- All cards unlocked from start

## 6. MVP Scope (Version 1.0)

### Must Have
- [x] Basic card system (10-15 cards)
- [x] 3-4 enemy types
- [x] Wave system
- [x] Shop between waves
- [x] Score tracking
- [x] Basic animations

### Future (Version 1.1+)
- [ ] More card types
- [ ] Boss enemies
- [ ] Power-ups during waves
- [ ] Leaderboards
- [ ] Achievements

## 7. Assets Needed

### Icons (SF Symbols)
- Card backs
- Attack/Defense/Power icons
- Enemy placeholders (skull, ghost, etc.)
- UI elements (coins, hearts, shields)

### Sounds (Future)
- Card play sound
- Attack sound
- Enemy defeat sound
- Background music
