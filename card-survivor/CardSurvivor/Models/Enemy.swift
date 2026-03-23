import Foundation

// MARK: - Enemy Model
struct Enemy: Identifiable {
    let id: UUID
    let name: String
    let nameEn: String
    var hp: Int
    let maxHp: Int
    let damage: Int
    let defense: Int
    let type: EnemyType
    var isPoisoned: Bool = false
    var poisonDamage: Int = 0
    var poisonTurns: Int = 0
    
    enum EnemyType: String, Codable {
        case basic      // Weak enemy
        case fast       // Low HP, attacks twice
        case tank       // High HP, slow
        case boss       // Appears every 5 waves
    }
    
    var icon: String {
        switch type {
        case .basic: return "skull"
        case .fast: return "bolt.fill"
        case .tank: return "shield.fill"
        case .boss: return "crown.fill"
        }
    }
    
    init(id: UUID = UUID(), name: String, nameEn: String, hp: Int, damage: Int, defense: Int = 0, type: EnemyType) {
        self.id = id
        self.name = name
        self.nameEn = nameEn
        self.hp = hp
        self.maxHp = hp
        self.damage = damage
        self.defense = defense
        self.type = type
    }
    
    mutating func takeDamage(_ damage: Int) -> Int {
        let actualDamage = max(1, damage - defense)
        hp = max(0, hp - actualDamage)
        return actualDamage
    }
    
    mutating func applyPoison(_ damage: Int, turns: Int) {
        isPoisoned = true
        poisonDamage = damage
        poisonTurns = turns
    }
    
    mutating func processPoison() {
        if isPoisoned && poisonTurns > 0 {
            hp = max(0, hp - poisonDamage)
            poisonTurns -= 1
            if poisonTurns <= 0 {
                isPoisoned = false
            }
        }
    }
    
    var isDead: Bool { hp <= 0 }
}

// MARK: - Sample Enemies
extension Enemy {
    static func generate(for wave: Int) -> [Enemy] {
        let count = min(3 + wave / 2, 8) // Max 8 enemies
        var enemies: [Enemy] = []
        
        for i in 0..<count {
            let enemyType: EnemyType
            let baseStats: (name: String, nameEn: String, hp: Int, dmg: Int, def: Int)
            
            // Every 5th wave is a boss wave
            if wave % 5 == 0 && i == 0 {
                enemyType = .boss
                baseStats = ("Demonio", "Demon", 50 + wave * 5, 15 + wave, 5)
            } else if wave > 3 && Int.random(in: 0...10) > 7 {
                enemyType = .fast
                baseStats = ("Murciélago", "Bat", 15 + wave, 5 + wave / 2, 0)
            } else if wave > 5 && Int.random(in: 0...10) > 8 {
                enemyType = .tank
                baseStats = ("Golem", "Golem", 30 + wave * 3, 8 + wave / 2, 3 + wave / 3)
            } else {
                enemyType = .basic
                baseStats = ("Zombi", "Zombie", 20 + wave * 2, 5 + wave / 2, 0)
            }
            
            enemies.append(Enemy(
                name: baseStats.name,
                nameEn: baseStats.nameEn,
                hp: baseStats.hp,
                damage: baseStats.dmg,
                defense: baseStats.def,
                type: enemyType
            ))
        }
        
        return enemies
    }
}
