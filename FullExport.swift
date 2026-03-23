import Foundation

/// Estructura completa para exportar/importar datos de MyBarTrack
struct FullExport: Codable {
    let version: String
    let exportDate: Date
    let bebidas: [BebidaExportItem]
    let consumiciones: [ConsumicionExportItem]?
    
    init(bebidas: [BebidaExportItem], consumiciones: [ConsumicionExportItem]? = nil) {
        self.version = "1.0"
        self.exportDate = Date()
        self.bebidas = bebidas
        self.consumiciones = consumiciones
    }
}

/// Item de bebida para exportación (igual que el existente)
struct BebidaExportItem: Codable, Identifiable {
    let id: UUID
    let nombre: String
    let emoji: String
    let precioBase: Double
    let categoria: String
    let orden: Int32
}

/// Item de consumición para exportación
struct ConsumicionExportItem: Codable, Identifiable {
    let id: UUID
    let bebidaId: UUID
    let cantidad: Int32
    let precioUnitario: Double
    let timestamp: Date
    let notas: String?
    
    init(from consumicion: Consumicion) {
        self.id = consumicion.id ?? UUID()
        self.bebidaId = consumicion.bebidaID ?? UUID()
        self.cantidad = consumicion.cantidad
        self.precioUnitario = consumicion.precioUnitario
        self.timestamp = consumicion.timestamp ?? Date()
        self.notas = consumicion.notas
    }
}

/// Modo de importación simple
enum ImportMode: String, CaseIterable {
    case reemplazarTodo = "Reemplazar todo"
    case añadirNuevo = "Añadir nuevo"
    
    var description: String {
        switch self {
        case .reemplazarTodo:
            return "Elimina todos los datos actuales y carga los nuevos"
        case .añadirNuevo:
            return "Añade los nuevos datos manteniendo los existentes"
        }
    }
}