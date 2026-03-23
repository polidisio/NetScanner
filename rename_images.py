#!/usr/bin/env python3
import os
import sys
from PIL import Image
import glob
import shutil

# Ruta a las imágenes
image_dir = "/Users/jmaudisio/Library/CloudStorage/OneDrive-Bibliotecascompartidas:Onedrive/Image Game"

# Categorías posibles para Card Survivor
categories = {
    'character': ['warrior', 'mage', 'rogue', 'paladin', 'knight', 'wizard', 'archer', 'priest'],
    'enemy': ['skeleton', 'zombie', 'ghost', 'vampire', 'demon', 'goblin', 'orc', 'dragon', 'beast'],
    'card': ['attack', 'defend', 'spell', 'heal', 'buff', 'debuff', 'fire', 'ice', 'lightning', 'shadow'],
    'background': ['castle', 'dungeon', 'forest', 'cave', 'ruins', 'temple', 'graveyard'],
    'ui': ['button', 'icon', 'border', 'frame', 'health', 'mana', 'energy']
}

def analyze_image(image_path):
    """Analiza una imagen y trata de determinar su contenido"""
    try:
        img = Image.open(image_path)
        
        # Obtener información básica
        width, height = img.size
        filename = os.path.basename(image_path)
        
        # Análisis simple de colores (para determinar tipo de imagen)
        colors = img.getcolors(maxcolors=10000)
        if colors:
            # Contar colores oscuros vs claros
            dark_count = 0
            light_count = 0
            for count, color in colors[:100]:  # Solo primeros 100 colores
                if color and len(color) >= 3:
                    r, g, b = color[:3]
                    brightness = (r + g + b) / 3
                    if brightness < 128:
                        dark_count += count
                    else:
                        light_count += count
            
            # Determinar tipo basado en colores y nombre
            is_dark = dark_count > light_count
            
            # Basado en el nombre del archivo original
            if 'unknown' in filename.lower():
                # Intentar determinar por número
                num_part = filename.lower().replace('unknown-', '').replace('.jpg', '').replace('.png', '')
                try:
                    num = int(num_part) if num_part.isdigit() else 0
                except:
                    num = 0
                
                # Asignar categorías basadas en número (esto es una estimación)
                if 2 <= num <= 5:
                    return 'character', f'character_{num}'
                elif 6 <= num <= 13:
                    return 'enemy', f'enemy_{num-5}'
                elif 14 <= num <= 21:
                    return 'card', f'card_{num-13}'
                elif 22 <= num <= 25:
                    return 'background', f'background_{num-21}'
                else:
                    return 'misc', f'image_{num}'
        
        return 'unknown', 'unknown'
        
    except Exception as e:
        print(f"Error analizando {image_path}: {e}")
        return 'error', 'error'

def rename_images():
    """Renombra todas las imágenes en el directorio"""
    # Encontrar todas las imágenes
    image_patterns = ['*.jpg', '*.jpeg', '*.png', '*.gif']
    image_files = []
    
    for pattern in image_patterns:
        image_files.extend(glob.glob(os.path.join(image_dir, pattern)))
    
    print(f"Encontradas {len(image_files)} imágenes")
    
    # Crear backup de nombres originales
    backup_file = os.path.join(image_dir, 'original_names.txt')
    with open(backup_file, 'w') as f:
        for img in sorted(image_files):
            f.write(f"{os.path.basename(img)}\n")
    
    # Renombrar imágenes
    renamed_count = 0
    for i, image_path in enumerate(sorted(image_files), 1):
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        
        # Analizar imagen
        category, base_name = analyze_image(image_path)
        
        # Crear nuevo nombre
        new_name = f"{base_name}{ext}"
        new_path = os.path.join(image_dir, new_name)
        
        # Si el nombre ya existe, añadir número
        counter = 1
        while os.path.exists(new_path):
            new_name = f"{base_name}_{counter}{ext}"
            new_path = os.path.join(image_dir, new_name)
            counter += 1
        
        # Renombrar
        try:
            os.rename(image_path, new_path)
            print(f"{i:2d}. {filename} -> {new_name} [{category}]")
            renamed_count += 1
        except Exception as e:
            print(f"Error renombrando {filename}: {e}")
    
    print(f"\nRenombradas {renamed_count} de {len(image_files)} imágenes")
    print(f"Backup de nombres originales en: {backup_file}")

if __name__ == "__main__":
    rename_images()