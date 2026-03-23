#!/usr/bin/env python3
import os
import glob
from PIL import Image
import json
import colorsys

# Ruta base
base_dir = "/Users/jmaudisio/Library/CloudStorage/OneDrive-Bibliotecascompartidas:Onedrive/Image Game"

def get_image_stats(image_path):
    """Obtiene estadísticas básicas de una imagen"""
    try:
        img = Image.open(image_path)
        width, height = img.size
        
        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Obtener colores dominantes
        pixels = list(img.getdata())
        total_pixels = len(pixels)
        
        # Analizar colores
        color_counts = {}
        for r, g, b in pixels[:10000]:  # Muestra de 10k píxeles
            # Clasificar por tono
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            # Determinar categoría de color
            if v < 0.2:
                color_cat = "black"
            elif v > 0.8 and s < 0.3:
                color_cat = "white"
            elif h < 0.05 or h > 0.95:
                color_cat = "red"
            elif h < 0.15:
                color_cat = "orange"
            elif h < 0.3:
                color_cat = "yellow"
            elif h < 0.5:
                color_cat = "green"
            elif h < 0.7:
                color_cat = "blue"
            elif h < 0.9:
                color_cat = "purple"
            else:
                color_cat = "pink"
            
            color_counts[color_cat] = color_counts.get(color_cat, 0) + 1
        
        # Encontrar color dominante
        if color_counts:
            dominant_color = max(color_counts.items(), key=lambda x: x[1])[0]
        else:
            dominant_color = "unknown"
        
        # Calcular brillo promedio
        brightness_sum = sum(r*0.299 + g*0.587 + b*0.114 for r, g, b in pixels[:10000])
        avg_brightness = brightness_sum / min(10000, total_pixels)
        
        # Determinar si es oscuro o claro
        brightness = "dark" if avg_brightness < 128 else "light"
        
        return {
            "size": f"{width}x{height}",
            "dominant_color": dominant_color,
            "brightness": brightness,
            "is_square": width == height
        }
        
    except Exception as e:
        return {"error": str(e)}

def guess_category(stats, folder_name):
    """Intenta adivinar la categoría basándose en estadísticas"""
    if folder_name == "characters":
        # Personajes suelen tener colores variados
        return "character"
    elif folder_name == "enemies":
        # Enemigos suelen ser oscuros
        if stats.get("brightness") == "dark":
            return "enemy"
        else:
            return "creature"
    elif folder_name == "cards":
        # Cartas pueden tener fondos más uniformes
        return "card"
    elif folder_name == "backgrounds":
        # Fondos suelen ser más anchos que altos (pero nuestras imágenes son cuadradas)
        return "background"
    else:
        return "unknown"

def generate_name(category, stats, index):
    """Genera un nombre basado en categoría y estadísticas"""
    color = stats.get("dominant_color", "unknown")
    brightness = stats.get("brightness", "medium")
    
    if category == "character":
        names = ["warrior", "mage", "rogue", "paladin", "knight", "archer", "priest"]
        return f"character_{names[index % len(names)]}.jpg"
    elif category == "enemy":
        names = ["skeleton", "zombie", "ghost", "vampire", "demon", "goblin", "orc", "dragon"]
        return f"enemy_{names[index % len(names)]}.jpg"
    elif category == "card":
        types = ["attack", "defend", "spell", "heal", "buff", "debuff", "fire", "ice", "lightning", "shadow"]
        return f"card_{types[index % len(types)]}.jpg"
    elif category == "background":
        types = ["castle", "dungeon", "forest", "cave", "ruins", "temple", "graveyard"]
        return f"background_{types[index % len(types)]}.jpg"
    else:
        return f"{category}_{index+1}.jpg"

def analyze_all():
    """Analiza todas las imágenes"""
    results = {}
    rename_plan = []
    
    folders = ["characters", "enemies", "cards", "backgrounds"]
    
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue
        
        print(f"\n=== {folder.upper()} ===")
        image_files = sorted(glob.glob(os.path.join(folder_path, "*.jpg")))
        
        folder_results = []
        for i, img_path in enumerate(image_files):
            filename = os.path.basename(img_path)
            print(f"Analizando: {filename}")
            
            stats = get_image_stats(img_path)
            category = guess_category(stats, folder)
            new_name = generate_name(category, stats, i)
            
            # Mostrar información
            print(f"  Tamaño: {stats.get('size', 'N/A')}")
            print(f"  Color dominante: {stats.get('dominant_color', 'N/A')}")
            print(f"  Brillo: {stats.get('brightness', 'N/A')}")
            print(f"  Sugerido: {new_name}")
            
            folder_results.append({
                "file": filename,
                "stats": stats,
                "suggested_name": new_name
            })
            
            rename_plan.append({
                "old": os.path.join(folder, filename),
                "new": os.path.join(folder, new_name)
            })
        
        results[folder] = folder_results
    
    # Guardar resultados
    output_file = os.path.join(base_dir, "simple_analysis.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Crear script de renombrado
    create_rename_script(rename_plan)
    
    print(f"\nAnálisis guardado en: {output_file}")

def create_rename_script(rename_plan):
    """Crea un script para renombrar"""
    script = "#!/bin/bash\n# Script de renombrado automático\n\n"
    script += f"cd \"{base_dir}\"\n\n"
    
    script += "echo 'Iniciando renombrado...'\n"
    
    for item in rename_plan:
        old = item["old"]
        new = item["new"]
        
        script += f"if [ -f \"{old}\" ]; then\n"
        script += f"  if [ -f \"{new}\" ]; then\n"
        script += f"    echo \"ERROR: {new} ya existe, saltando {old}\"\n"
        script += "  else\n"
        script += f"    mv \"{old}\" \"{new}\"\n"
        script += f"    echo \"OK: {old} -> {new}\"\n"
        script += "  fi\n"
        script += "else\n"
        script += f"  echo \"ERROR: {old} no encontrado\"\n"
        script += "fi\n"
    
    script += "\necho 'Renombrado completado.'\n"
    
    script_file = os.path.join(base_dir, "auto_rename.sh")
    with open(script_file, "w") as f:
        f.write(script)
    
    os.chmod(script_file, 0o755)
    print(f"Script creado: {script_file}")
    print(f"Ejecutar con: cd \"{base_dir}\" && ./auto_rename.sh")

if __name__ == "__main__":
    analyze_all()