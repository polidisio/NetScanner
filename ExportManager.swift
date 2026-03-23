import Foundation
import CoreData

/// Manager unificado para exportación e importación
class ExportManager {
    static let shared = ExportManager()
    
    private let fileExtension = "mybartrack"
    private let currentVersion = "1.0"
    
    // MARK: - Exportación
    
    /// Exporta todas las bebidas y opcionalmente el historial
    func exportFullData(includeHistorial: Bool = false) -> URL? {
        let bebidas = fetchBebidasForExport()
        let consumiciones = includeHistorial ? fetchConsumicionesForExport() : nil
        
        let fullExport = FullExport(
            bebidas: bebidas,
            consumiciones: consumiciones
        )
        
        return saveExportToFile(fullExport)
    }
    
    /// Exporta solo bebidas (compatible con versión anterior)
    func exportBebidasOnly() -> URL? {
        let bebidas = fetchBebidasForExport()
        let fullExport = FullExport(bebidas: bebidas, consumiciones: nil)
        return saveExportToFile(fullExport)
    }
    
    // MARK: - Importación
    
    /// Importa desde un archivo .mybartrack
    func importFromFile(_ url: URL, mode: ImportMode, completion: @escaping (Result<ImportSummary, Error>) -> Void) {
        do {
            let data = try Data(contentsOf: url)
            let fullExport = try JSONDecoder().decode(FullExport.self, from: data)
            
            // Validar versión
            guard fullExport.version == currentVersion else {
                throw ImportError.versionMismatch(exportedVersion: fullExport.version, currentVersion: currentVersion)
            }
            
            // Ejecutar importación en background
            DispatchQueue.global(qos: .userInitiated).async {
                let result = self.executeImport(fullExport, mode: mode)
                DispatchQueue.main.async {
                    completion(result)
                }
            }
            
        } catch {
            completion(.failure(error))
        }
    }
    
    // MARK: - Private Methods
    
    private func fetchBebidasForExport() -> [BebidaExportItem] {
        let bebidas = CoreDataManager.shared.fetchBebidas()
        return bebidas.map { bebida in
            BebidaExportItem(
                id: bebida.id ?? UUID(),
                nombre: bebida.nombre ?? "",
                emoji: bebida.emoji ?? "",
                precioBase: bebida.precioBase,
                categoria: bebida.categoria ?? "",
                orden: bebida.orden
            )
        }
    }
    
    private func fetchConsumicionesForExport() -> [ConsumicionExportItem] {
        let request: NSFetchRequest<Consumicion> = Consumicion.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(key: "timestamp", ascending: false)]
        
        do {
            let consumiciones = try CoreDataManager.shared.context.fetch(request)
            return consumiciones.map { ConsumicionExportItem(from: $0) }
        } catch {
            print("Error fetching consumiciones for export: \(error)")
            return []
        }
    }
    
    private func saveExportToFile(_ fullExport: FullExport) -> URL? {
        guard let jsonData = try? JSONEncoder().encode(fullExport) else {
            print("Error encoding export data")
            return nil
        }
        
        let tempDir = FileManager.default.temporaryDirectory
        let fileName = "MyBarTrack_\(Date().ISO8601Format()).\(fileExtension)"
        let fileURL = tempDir.appendingPathComponent(fileName)
        
        do {
            try jsonData.write(to: fileURL)
            return fileURL
        } catch {
            print("Error writing export file: \(error)")
            return nil
        }
    }
    
    private func executeImport(_ fullExport: FullExport, mode: ImportMode) -> Result<ImportSummary, Error> {
        let context = CoreDataManager.shared.context
        
        do {
            var summary = ImportSummary()
            
            switch mode {
            case .reemplazarTodo:
                // 1. Borrar todo existente
                deleteAllBebidas(in: context)
                deleteAllConsumiciones(in: context)
                
                // 2. Importar nuevo
                summary.bebidasImported = importBebidas(fullExport.bebidas, context: context)
                if let consumiciones = fullExport.consumiciones {
                    summary.consumicionesImported = importConsumiciones(consumiciones, context: context)
                }
                
            case .añadirNuevo:
                // 1. Importar solo bebidas nuevas (por nombre)
                summary.bebidasImported = importBebidasSoloNuevas(fullExport.bebidas, context: context)
                
                // 2. Importar todas las consumiciones (asumimos no hay duplicados exactos)
                if let consumiciones = fullExport.consumiciones {
                    summary.consumicionesImported = importConsumiciones(consumiciones, context: context)
                }
            }
            
            // 3. Guardar cambios
            try context.save()
            return .success(summary)
            
        } catch {
            return .failure(error)
        }
    }
    
    private func importBebidas(_ bebidas: [BebidaExportItem], context: NSManagedObjectContext) -> Int {
        var count = 0
        for bebidaItem in bebidas {
            let bebida = Bebida(context: context)
            bebida.id = UUID() // Nuevo UUID para evitar colisiones
            bebida.nombre = bebidaItem.nombre
            bebida.emoji = bebidaItem.emoji
            bebida.precioBase = bebidaItem.precioBase
            bebida.categoria = bebidaItem.categoria
            bebida.orden = bebidaItem.orden
            count += 1
        }
        return count
    }
    
    private func importBebidasSoloNuevas(_ bebidas: [BebidaExportItem], context: NSManagedObjectContext) -> Int {
        // Obtener nombres de bebidas existentes
        let existingRequest: NSFetchRequest<Bebida> = Bebida.fetchRequest()
        let existingBebidas = (try? context.fetch(existingRequest)) ?? []
        let existingNames = Set(existingBebidas.compactMap { $0.nombre })
        
        var count = 0
        for bebidaItem in bebidas {
            // Solo importar si el nombre no existe
            if !existingNames.contains(bebidaItem.nombre) {
                let bebida = Bebida(context: context)
                bebida.id = UUID()
                bebida.nombre = bebidaItem.nombre
                bebida.emoji = bebidaItem.emoji
                bebida.precioBase = bebidaItem.precioBase
                bebida.categoria = bebidaItem.categoria
                bebida.orden = bebidaItem.orden
                count += 1
            }
        }
        return count
    }
    
    private func importConsumiciones(_ consumiciones: [ConsumicionExportItem], context: NSManagedObjectContext) -> Int {
        // NOTA: Esto importa todas las consumiciones sin verificar duplicados
        // En una versión futura podríamos verificar por timestamp + bebidaId
        var count = 0
        for consumicionItem in consumiciones {
            let consumicion = Consumicion(context: context)
            consumicion.id = UUID() // Nuevo UUID
            consumicion.bebidaID = consumicionItem.bebidaId
            consumicion.cantidad = consumicionItem.cantidad
            consumicion.precioUnitario = consumicionItem.precioUnitario
            consumicion.timestamp = consumicionItem.timestamp
            consumicion.notas = consumicionItem.notas
            count += 1
        }
        return count
    }
    
    private func deleteAllBebidas(in context: NSManagedObjectContext) {
        let request: NSFetchRequest<NSFetchRequestResult> = Bebida.fetchRequest()
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
        
        do {
            try context.execute(deleteRequest)
        } catch {
            print("Error deleting bebidas: \(error)")
        }
    }
    
    private func deleteAllConsumiciones(in context: NSManagedObjectContext) {
        let request: NSFetchRequest<NSFetchRequestResult> = Consumicion.fetchRequest()
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: request)
        
        do {
            try context.execute(deleteRequest)
        } catch {
            print("Error deleting consumiciones: \(error)")
        }
    }
}

// MARK: - Supporting Types

struct ImportSummary {
    var bebidasImported: Int = 0
    var consumicionesImported: Int = 0
    
    var description: String {
        var parts: [String] = []
        if bebidasImported > 0 {
            parts.append("\(bebidasImported) bebidas")
        }
        if consumicionesImported > 0 {
            parts.append("\(consumicionesImported) consumiciones")
        }
        return parts.joined(separator: " y ")
    }
}

enum ImportError: LocalizedError {
    case versionMismatch(exportedVersion: String, currentVersion: String)
    
    var errorDescription: String? {
        switch self {
        case .versionMismatch(let exportedVersion, let currentVersion):
            return "Versión incompatible. Archivo: \(exportedVersion), App: \(currentVersion)"
        }
    }
}