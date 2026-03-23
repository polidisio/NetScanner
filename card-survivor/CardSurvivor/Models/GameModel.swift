import Foundation

// MARK: - Game State
enum GameState {
    case menu
    case playing
    case shop
    case waveComplete
    case gameOver
}

// MARK: - Game Model
class GameModel: ObservableObject {
    @Published var state: GameState = .menu
    @Published var player: Player = Player()
    @Published var enemies: [Enemy] = []
    @Published var wave: Int = 1
    @Published var score: Int = 0
    @Published var selectedCard: Card?
    @Published var selectedEnemy: Enemy?
    @Published var message: String = ""
    @Published var showMessage: Bool = false
    
    // High score
    var highScore: Int {
        get { UserDefaults.standard.integer(forKey: "highScore") }
        set { UserDefaults.standard.set(newValue, forKey: "highScore") }
    }
    
    // Shop cards
    var shopCards: [Card] = []
    
    func startNewGame() {
        player = Player()
        enemies = Enemy.generate(for: 1)
        wave = 1
        score = 0
        player state = .playing.startTurn()
       
    }
    
    func startNextWave() {
        wave += 1
        enemies = Enemy.generate(for: wave)
        player.startTurn()
        state = .playing
    }
    
    func playCard(_ card: Card) {
        guard let targetEnemy = selectedEnemy, card.type == .attack else {
            // For defense/power, no target needed
            if card.type == .defense {
                player.heal(card.value)
                showTemporaryMessage("+❤️ \(card.value)")
            } else if card.type == .power {
                if card.name.contains("Veneno") || card.nameEn.contains("Poison") {
                    // Apply poison to first enemy
                    if !enemies.isEmpty {
                        enemies[0].applyPoison(card.value, turns: 3)
                        showTemporaryMessage("☠️ Veneno!")
                    }
                } else if card.name.contains("Furia") || card.nameEn.contains("Rage") {
                    player.damageBuff += card.value
                    player.damageBuffTurns = 3
                    showTemporaryMessage("⚔️ +\(card.value) dmg!")
                } else if card.name.contains("Curación") || card.nameEn.contains("Heal") {
                    player.heal(card.value)
                    showTemporaryMessage("❤️ +\(card.value)")
                }
            }
            
            player.discardPile.append(card)
            if let index = player.hand.firstIndex(where: { $0.id == card.id }) {
                player.hand.remove(at: index)
            }
            
            checkEndTurn()
            return
        }
        
        // Attack card with target
        let damage = card.value + player.damageBuff
        let actualDamage = targetEnemy.takeDamage(damage)
        
        // Remove card from hand
        player.discardPile.append(card)
        if let index = player.hand.firstIndex(where: { $0.id == card.id }) {
            player.hand.remove(at: index)
        }
        
        // Check if enemy died
        if targetEnemy.isDead {
            score += targetEnemy.type == .boss ? 100 : 10
            player.gold += targetEnemy.type == .boss ? 50 : 5
            enemies.removeAll { $0.id == targetEnemy.id }
            showTemporaryMessage("💀 +\(targetEnemy.type == .boss ? 50 : 5) gold!")
        } else {
            showTemporaryMessage("⚔️ \(actualDamage) dmg!")
        }
        
        selectedEnemy = nil
        checkEndTurn()
    }
    
    func enemyTurn() {
        // Process poison on all enemies
        for i in enemies.indices {
            enemies[i].processPoison()
        }
        
        // Remove dead enemies from poison
        enemies.removeAll { $0.isDead }
        
        // Enemies attack
        for enemy in enemies {
            let damage = enemy.damage
            player.takeDamage(damage)
        }
        
        if player.isDead {
            gameOver()
        } else {
            player.endTurn()
            player.startTurn()
        }
    }
    
    func checkEndTurn() {
        // Check if all enemies are dead
        if enemies.isEmpty {
            waveComplete()
        } else if player.energy <= 0 || player.hand.isEmpty {
            enemyTurn()
        }
    }
    
    func waveComplete() {
        score += wave * 50
        player.gold += wave * 10
        
        // Generate shop cards
        shopCards = Card.sampleCards.shuffled().prefix(6).map { $0 }
        
        state = .shop
    }
    
    func gameOver() {
        if score > highScore {
            highScore = score
        }
        state = .gameOver
    }
    
    func buyCard(_ card: Card) {
        if player.gold >= card.cost * 10 {
            player.gold -= card.cost * 10
            player.addCardToDeck(card)
            shopCards.removeAll { $0.id == card.id }
            showTemporaryMessage("✅ Comprado!")
        } else {
            showTemporaryMessage("💰 No tienes suficiente oro!")
        }
    }
    
    private func showTemporaryMessage(_ msg: String) {
        message = msg
        showMessage = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
            self?.showMessage = false
        }
    }
}
