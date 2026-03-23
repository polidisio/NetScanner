import Foundation
import CoreData

class BebidaExporter {
    static let shared = BebidaExporter()
    
    private let exportVersion = "1.0"
    
    // MARK: - Métodos existentes (mantener compatibilidad)
    
    func exportBebidas(_ bebidas: [BebidaExportItem]) -> URL? {
        let data = BebidaExportData(version: exportVersion, exportDate: Date(), bebidas: bebidas)
        
        guard let jsonData = try? JSONEncoder().encode(data) else {
            return nil
        }
        
        let tempDir = FileManager.default.temporaryDirectory
        let fileURL = tempDir.appendingPathComponent("bebidas.json")
        
        do {
            try jsonData.write(to: fileURL)
            return fileURL
        } catch {
            print("Error writing export file: \(error)")
            return nil
        }
    }
    
    func createExportItem(from bebida: Bebida) -> BebidaExportItem {
        BebidaExportItem(
            id: bebida.id ?? UUID(),
            nombre: bebida.nombre ?? "",
            emoji: bebida.emoji ?? "",
            precioBase: bebida.precioBase,
            categoria: bebida.categoria ?? "",
            orden: bebida.orden
        )
    }
    
    // MARK: - Nuevos métodos usando ExportManager
    
    /// Exporta todas las bebidas (nuevo método)
    func exportAllBebidas() -> URL? {
        let bebidas = CoreDataManager.shared.fetchBebidas()
        let exportItems = bebidas.map { createExportItem(from: $0) }
        return exportBebidas(exportItems)
    }
    
    /// Método de conveniencia para usar el nuevo ExportManager
    func exportFullData(includeHistorial: Bool = false) -> URL? {
        return ExportManager.shared.exportFullData(includeHistorial: includeHistorial)
    }
}

// MARK: - Estructuras existentes (mantener para compatibilidad)

struct BebidaExportData: Codable {
    let version: String
    let exportDate: Date
    let bebidas: [BebidaExportItem]
}

// BebidaExportItem ahora está definido en FullExport.swift
// Pero mantenemos un typealias para compatibilidad
typealias BebidaExportItem = BebidaExportItem