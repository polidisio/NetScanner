import Foundation

// MARK: - Player Model
struct Player {
    var hp: Int
    let maxHp: Int
    var gold: Int
    var deck: [Card]
    var hand: [Card]
    var discardPile: [Card]
    var drawPile: [Card]
    var energy: Int
    let maxEnergy: Int
    var damageBuff: Int = 0
    var damageBuffTurns: Int = 0
    
    init(maxHp: Int = 50, maxEnergy: Int = 3) {
        self.hp = maxHp
        self.maxHp = maxHp
        self.gold = 0
        self.deck = Card.sampleCards
        self.hand = []
        self.discardPile = []
        self.drawPile = Card.sampleCards.shuffled()
        self.energy = maxEnergy
        self.maxEnergy = maxEnergy
    }
    
    mutating func startTurn() {
        energy = maxEnergy
        damageBuff = 0
        damageBuffTurns = 0
        
        // Draw cards
        drawCards(5)
    }
    
    mutating func drawCards(_ count: Int) {
        for _ in 0..<count {
            if drawPile.isEmpty {
                // Shuffle discard into draw
                drawPile = discardPile.shuffled()
                discardPile.removeAll()
            }
            
            if !drawPile.isEmpty && hand.count < 8 {
                hand.append(drawPile.removeFirst())
            }
        }
    }
    
    mutating func playCard(_ card: Card, target: Enemy?) -> CardPlayResult {
        guard energy >= card.cost else {
            return .notEnoughEnergy
        }
        
        energy -= card.cost
        
        // Remove from hand
        if let index = hand.firstIndex(where: { $0.id == card.id }) {
            hand.remove(at: index)
            discardPile.append(card)
        }
        
        switch card.type {
        case .attack:
            return .attack(card, card.value + damageBuff, target)
        case .defense:
            return .defense(card, card.value)
        case .power:
            return .power(card, card.value)
        }
    }
    
    mutating func endTurn() {
        // Return hand to discard
        discardPile.append(contentsOf: hand)
        hand.removeAll()
        
        // Process damage buff
        if damageBuffTurns > 0 {
            damageBuffTurns -= 1
            if damageBuffTurns <= 0 {
                damageBuff = 0
            }
        }
    }
    
    mutating func takeDamage(_ damage: Int) {
        hp = max(0, hp - damage)
    }
    
    mutating func heal(_ amount: Int) {
        hp = min(maxHp, hp + amount)
    }
    
    mutating func addGold(_ amount: Int) {
        gold += amount
    }
    
    mutating func addCardToDeck(_ card: Card) {
        deck.append(card)
    }
    
    mutating func removeCardFromDeck(_ card: Card) {
        deck.removeAll { $0.id == card.id }
    }
    
    var isDead: Bool { hp <= 0 }
}

enum CardPlayResult {
    case attack(Card, Int, Enemy?)
    case defense(Card, Int)
    case power(Card, Int)
    case notEnoughEnergy
}
