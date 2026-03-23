import Foundation

// MARK: - Card Model
struct Card: Identifiable, Codable, Equatable {
    let id: UUID
    let name: String
    let nameEn: String
    let description: String
    let descriptionEn: String
    let type: CardType
    let cost: Int
    let value: Int // Damage, block, or heal amount
    let rarity: CardRarity
    
    enum CardType: String, Codable {
        case attack
        case defense
        case power
    }
    
    enum CardRarity: String, Codable {
        case common
        case uncommon
        case rare
    }
    
    init(id: UUID = UUID(), name: String, nameEn: String, description: String, descriptionEn: String, type: CardType, cost: Int, value: Int, rarity: CardRarity) {
        self.id = id
        self.name = name
        self.nameEn = nameEn
        self.description = description
        self.descriptionEn = descriptionEn
        self.type = type
        self.cost = cost
        self.value = value
        self.rarity = rarity
    }
}

// MARK: - Sample Cards
extension Card {
    static let sampleCards: [Card] = [
        // Attack Cards
        Card(name: "Golpe", nameEn: "Strike", 
             description: "Inflige 6 de daño", descriptionEn: "Deal 6 damage",
             type: .attack, cost: 1, value: 6, rarity: .common),
        Card(name: "Corte", nameEn: "Slash",
             description: "Inflige 10 de daño", descriptionEn: "Deal 10 damage",
             type: .attack, cost: 2, value: 10, rarity: .common),
        Card(name: "Estocada", nameEn: "Thrust",
             description: "Inflige 15 de daño", descriptionEn: "Deal 15 damage",
             type: .attack, cost: 3, value: 15, rarity: .uncommon),
        Card(name: "Frenesí", nameEn: "Frenzy",
             description: "Inflige 25 de daño", descriptionEn: "Deal 25 damage",
             type: .attack, cost: 4, value: 25, rarity: .rare),
        
        // Defense Cards
        Card(name: "Escudo", nameEn: "Shield",
             description: "Bloquea 5 de daño", descriptionEn: "Block 5 damage",
             type: .defense, cost: 1, value: 5, rarity: .common),
        Card(name: "Pared", nameEn: "Wall",
             description: "Bloquea 10 de daño", descriptionEn: "Block 10 damage",
             type: .defense, cost: 2, value: 10, rarity: .common),
        Card(name: "Refugio", nameEn: "Refuge",
             description: "Bloquea 15 de daño", descriptionEn: "Block 15 damage",
             type: .defense, cost: 3, value: 15, rarity: .uncommon),
        
        // Power Cards
        Card(name: "Veneno", nameEn: "Poison",
             description: "Envenena al enemigo (3 dmg/turno)", descriptionEn: "Poison enemy (3 dmg/turn)",
             type: .power, cost: 2, value: 3, rarity: .uncommon),
        Card(name: "Curación", nameEn: "Heal",
             description: "Cura 10 HP", descriptionEn: "Heal 10 HP",
             type: .power, cost: 2, value: 10, rarity: .uncommon),
        Card(name: "Furia", nameEn: "Rage",
             description: "+5 daño durante 3 turnos", descriptionEn: "+5 damage for 3 turns",
             type: .power, cost: 3, value: 5, rarity: .rare),
    ]
}
