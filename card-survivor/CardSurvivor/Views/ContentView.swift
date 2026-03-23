import SwiftUI

struct ContentView: View {
    @StateObject private var game = GameModel()
    
    var body: some View {
        ZStack {
            // Background
            Color(hex: "1C1C1E")
                .ignoresSafeArea()
            
            switch game.state {
            case .menu:
                MenuView(game: game)
            case .playing:
                GameView(game: game)
            case .shop:
                ShopView(game: game)
            case .waveComplete:
                WaveCompleteView(game: game)
            case .gameOver:
                GameOverView(game: game)
            }
        }
        .preferredColorScheme(.dark)
    }
}

// MARK: - Menu View
struct MenuView: View {
    @ObservedObject var game: GameModel
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            // Title
            VStack(spacing: 10) {
                Text("CARD")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(Color(hex: "BF5AF2"))
                
                Text("SURVIVOR")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(.white)
            }
            
            // High Score
            if game.highScore > 0 {
                Text("High Score: \(game.highScore)")
                    .font(.title3)
                    .foregroundColor(Color(hex: "FFD60A"))
            }
            
            Spacer()
            
            // Play Button
            Button(action: {
                game.startNewGame()
            }) {
                Text("PLAY")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .frame(width: 200, height: 60)
                    .background(Color(hex: "BF5AF2"))
                    .cornerRadius(15)
            }
            
            Spacer()
            
            // Credits
            Text("v1.0")
                .foregroundColor(.gray)
                .padding(.bottom, 20)
        }
    }
}

// MARK: - Game View
struct GameView: View {
    @ObservedObject var game: GameModel
    
    var body: some View {
        VStack(spacing: 0) {
            // Top Bar
            HStack {
                Text("Wave \(game.wave)")
                    .font(.headline)
                    .foregroundColor(.white)
                
                Spacer()
                
                HStack(spacing: 20) {
                    // Gold
                    HStack {
                        Image(systemName: "dollarsign.circle.fill")
                            .foregroundColor(Color(hex: "FFD60A"))
                        Text("\(game.player.gold)")
                            .foregroundColor(Color(hex: "FFD60A"))
                    }
                    
                    // Score
                    Text("Score: \(game.score)")
                        .foregroundColor(.white)
                }
            }
            .padding()
            .background(Color(hex: "2C2C2E"))
            
            // Enemy Area
            ZStack {
                // Enemies
                HStack(spacing: 20) {
                    ForEach(game.enemies) { enemy in
                        EnemyView(enemy: enemy, isSelected: game.selectedEnemy?.id == enemy.id)
                            .onTapGesture {
                                if game.selectedEnemy?.id == enemy.id {
                                    game.selectedEnemy = nil
                                } else {
                                    game.selectedEnemy = enemy
                                }
                            }
                    }
                }
                
                // Message overlay
                if game.showMessage {
                    Text(game.message)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(10)
                        .transition(.scale)
                }
            }
            .frame(maxHeight: .infinity)
            .background(Color(hex: "1C1C1E"))
            
            // Player Stats
            HStack {
                // HP
                HStack {
                    Image(systemName: "heart.fill")
                        .foregroundColor(.red)
                    Text("\(game.player.hp)/\(game.player.maxHp)")
                        .foregroundColor(.white)
                }
                
                Spacer()
                
                // Energy
                HStack(spacing: 5) {
                    ForEach(0..<game.player.maxEnergy, id: \.self) { index in
                        Image(systemName: index < game.player.energy ? "bolt.fill" : "bolt")
                            .foregroundColor(index < game.player.energy ? Color(hex: "FFD60A") : .gray)
                    }
                }
                
                Spacer()
                
                // Buff indicator
                if game.player.damageBuff > 0 {
                    Text("⚔️+\(game.player.damageBuff)")
                        .foregroundColor(.red)
                }
                
                // End Turn Button
                Button(action: {
                    game.enemyTurn()
                }) {
                    Text("End Turn")
                        .font(.caption)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.gray.opacity(0.3))
                        .cornerRadius(5)
                }
            }
            .padding()
            .background(Color(hex: "2C2C2E"))
            
            // Hand
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(game.player.hand) { card in
                        CardView(card: card)
                            .onTapGesture {
                                game.playCard(card)
                            }
                    }
                }
                .padding()
            }
            .frame(height: 160)
            .background(Color(hex: "2C2C2E"))
        }
    }
}

// MARK: - Shop View
struct ShopView: View {
    @ObservedObject var game: GameModel
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            HStack {
                Text("SHOP")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                Spacer()
                
                HStack {
                    Image(systemName: "dollarsign.circle.fill")
                        .foregroundColor(Color(hex: "FFD60A"))
                    Text("\(game.player.gold)")
                        .foregroundColor(Color(hex: "FFD60A"))
                        .font(.title2)
                }
            }
            .padding()
            
            // Cards to buy
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
                ForEach(game.shopCards) { card in
                    CardView(card: card, showPrice: true, price: card.cost * 10)
                        .onTapGesture {
                            game.buyCard(card)
                        }
                }
            }
            .padding()
            
            Spacer()
            
            // Continue Button
            Button(action: {
                game.startNextWave()
            }) {
                Text("Next Wave →")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color(hex: "BF5AF2"))
                    .cornerRadius(15)
            }
            .padding()
        }
        .background(Color(hex: "1C1C1E"))
    }
}

// MARK: - Wave Complete View
struct WaveCompleteView: View {
    @ObservedObject var game: GameModel
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Text("WAVE \(game.wave) COMPLETE!")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(Color(hex: "FFD60A"))
            
            VStack(spacing: 10) {
                Text("Score: \(game.score)")
                    .font(.title)
                    .foregroundColor(.white)
                
                Text("Gold: \(game.player.gold)")
                    .font(.title2)
                    .foregroundColor(Color(hex: "FFD60A"))
            }
            
            Spacer()
            
            Button(action: {
                game.startNextWave()
            }) {
                Text("Continue")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .frame(width: 200, height: 50)
                    .background(Color(hex: "BF5AF2"))
                    .cornerRadius(15)
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(hex: "1C1C1E"))
    }
}

// MARK: - Game Over View
struct GameOverView: View {
    @ObservedObject var game: GameModel
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Text("GAME OVER")
                .font(.system(size: 48, weight: .bold))
                .foregroundColor(.red)
            
            VStack(spacing: 10) {
                Text("Waves: \(game.wave)")
                    .font(.title)
                    .foregroundColor(.white)
                
                Text("Score: \(game.score)")
                    .font(.title2)
                    .foregroundColor(Color(hex: "BF5AF2"))
                
                if game.score >= game.highScore {
                    Text("🎉 NEW HIGH SCORE! 🎉")
                        .foregroundColor(Color(hex: "FFD60A"))
                }
            }
            
            Spacer()
            
            VStack(spacing: 15) {
                Button(action: {
                    game.startNewGame()
                }) {
                    Text("Play Again")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .frame(width: 200, height: 50)
                        .background(Color(hex: "BF5AF2"))
                        .cornerRadius(15)
                }
                
                Button(action: {
                    game.state = .menu
                }) {
                    Text("Menu")
                        .font(.title2)
                        .foregroundColor(.white)
                        .frame(width: 200, height: 50)
                        .background(Color.gray.opacity(0.3))
                        .cornerRadius(15)
                }
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(hex: "1C1C1E"))
    }
}

// MARK: - Card View
struct CardView: View {
    let card: Card
    var showPrice: Bool = false
    var price: Int = 0
    
    var body: some View {
        VStack(spacing: 5) {
            // Card type indicator
            HStack {
                Image(systemName: card.type == .attack ? "bolt.fill" : (card.type == .defense ? "shield.fill" : "star.fill")
                    .foregroundColor(cardColor)
                    .font(.caption)
                
                Spacer()
                
                if showPrice {
                    Text("\(price)💰")
                        .font(.caption2)
                        .foregroundColor(Color(hex: "FFD60A"))
                } else {
                    Text("\(card.cost)")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(cardColor)
                }
            }
            
            // Name
            Text(card.name)
                .font(.caption)
                .fontWeight(.bold)
                .foregroundColor(.white)
                .lineLimit(1)
            
            // Value
            Text(card.value > 0 ? "\(card.value)" : "")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(cardColor)
            
            // Description
            Text(card.description)
                .font(.caption2)
                .foregroundColor(.gray)
                .lineLimit(2)
                .multilineTextAlignment(.center)
        }
        .padding(10)
        .frame(width: 100, height: 140)
        .background(cardBackground)
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(cardColor.opacity(0.5), lineWidth: 2)
        )
    }
    
    var cardColor: Color {
        switch card.type {
        case .attack: return Color(hex: "FF453A")
        case .defense: return Color(hex: "0A84FF")
        case .power: return Color(hex: "BF5AF2")
        }
    }
    
    var cardBackground: Color {
        switch card.rarity {
        case .common: return Color(hex: "2C2C2E")
        case .uncommon: return Color(hex: "3C3C3E")
        case .rare: return Color(hex: "4C4C4E")
        }
    }
}

// MARK: - Enemy View
struct EnemyView: View {
    let enemy: Enemy
    let isSelected: Bool
    
    var body: some View {
        VStack(spacing: 5) {
            // Icon
            Image(systemName: enemy.icon)
                .font(.system(size: 40))
                .foregroundColor(enemyColor)
            
            // Name
            Text(enemy.name)
                .font(.caption)
                .foregroundColor(.white)
            
            // HP Bar
            HStack {
                Image(systemName: "heart.fill")
                    .font(.caption2)
                    .foregroundColor(.red)
                
                Text("\(enemy.hp)/\(enemy.maxHp)")
                    .font(.caption2)
                    .foregroundColor(.white)
            }
            
            // Poison indicator
            if enemy.isPoisoned {
                HStack(spacing: 2) {
                    Image(systemName: "flame.fill")
                        .font(.caption2)
                        .foregroundColor(.green)
                    Text("\(enemy.poisonDamage)x\(enemy.poisonTurns)")
                        .font(.caption2)
                        .foregroundColor(.green)
                }
            }
        }
        .padding(10)
        .background(isSelected ? Color.white.opacity(0.2) : Color(hex: "2C2C2E"))
        .cornerRadius(10)
        .overlay(
            RoundedRectangle(cornerRadius: 10)
                .stroke(isSelected ? Color.white : Color.clear, lineWidth: 2)
        )
    }
    
    var enemyColor: Color {
        switch enemy.type {
        case .basic: return .gray
        case .fast: return .yellow
        case .tank: return .blue
        case .boss: return .red
        }
    }
}

// MARK: - Color Extension
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

#Preview {
    ContentView()
}
