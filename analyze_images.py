#!/usr/bin/env python3
import os
import glob
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import json

# Ruta a las imágenes
base_dir = "/Users/jmaudisio/Library/CloudStorage/OneDrive-Bibliotecascompartidas:Onedrive/Image Game"

# Cargar modelo CLIP
print("Cargando modelo CLIP...")
try:
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(device)
    print(f"Modelo cargado en dispositivo: {device}")
except Exception as e:
    print(f"Error cargando modelo CLIP: {e}")
    print("Usando análisis básico...")
    model = None

# Categorías para Card Survivor
categories = {
    "characters": [
        "a warrior in heavy armor with a sword",
        "a mage in robes with a magical staff", 
        "a rogue in cloak with daggers",
        "a paladin in shining armor with a hammer",
        "a knight in armor",
        "a wizard with spellbook",
        "an archer with bow",
        "a priest with holy symbol"
    ],
    "enemies": [
        "a skeleton warrior with sword",
        "a zombie rotting creature",
        "a ghost transparent spirit",
        "a vampire with cape and fangs",
        "a demon with horns",
        "a goblin green creature with club",
        "an orc muscular with axe",
        "a dragon scaly creature",
        "a beast monster",
        "a dark creature"
    ],
    "cards": [
        "a sword attack card",
        "a shield defense card",
        "a fire spell card",
        "an ice magic card",
        "a lightning spell card",
        "a healing potion card",
        "a buff enhancement card",
        "a debuff curse card",
        "a magical rune",
        "a spellbook"
    ],
    "backgrounds": [
        "a gothic castle background",
        "a dungeon interior",
        "a dark forest",
        "a cave interior",
        "ancient ruins",
        "a temple interior",
        "a graveyard at night",
        "a dark fantasy landscape"
    ]
}

def analyze_image_with_clip(image_path, category):
    """Analiza una imagen usando CLIP"""
    if model is None:
        return "unknown", 0.0
    
    try:
        image = Image.open(image_path)
        
        # Procesar imagen y textos
        inputs = processor(
            text=categories[category], 
            images=image, 
            return_tensors="pt", 
            padding=True
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Obtener predicciones
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Obtener similitudes
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
        
        # Encontrar la mejor coincidencia
        best_idx = probs.argmax().item()
        best_prob = probs[0][best_idx].item()
        best_description = categories[category][best_idx]
        
        return best_description, best_prob
        
    except Exception as e:
        print(f"Error analizando {image_path}: {e}")
        return "error", 0.0

def analyze_all_images():
    """Analiza todas las imágenes en todas las carpetas"""
    results = {}
    
    for category in ["characters", "enemies", "cards", "backgrounds"]:
        category_dir = os.path.join(base_dir, category)
        if not os.path.exists(category_dir):
            continue
            
        print(f"\nAnalizando {category}...")
        image_files = glob.glob(os.path.join(category_dir, "*.jpg"))
        
        category_results = []
        for img_path in sorted(image_files):
            filename = os.path.basename(img_path)
            print(f"  Analizando {filename}...")
            
            description, confidence = analyze_image_with_clip(img_path, category)
            
            category_results.append({
                "file": filename,
                "description": description,
                "confidence": confidence,
                "suggested_name": generate_suggested_name(description, category)
            })
            
            print(f"    -> {description} ({confidence:.2%})")
        
        results[category] = category_results
    
    # Guardar resultados
    output_file = os.path.join(base_dir, "image_analysis.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResultados guardados en: {output_file}")
    
    # Generar sugerencias de renombrado
    generate_rename_suggestions(results)

def generate_suggested_name(description, category):
    """Genera un nombre de archivo sugerido basado en la descripción"""
    # Limpiar la descripción
    clean_desc = description.lower()
    clean_desc = clean_desc.replace("a ", "").replace("an ", "")
    clean_desc = clean_desc.replace(" with ", "_").replace(" in ", "_")
    clean_desc = clean_desc.replace(" ", "_").replace(",", "").replace(".", "")
    
    # Acortar si es muy largo
    if len(clean_desc) > 30:
        words = clean_desc.split("_")
        clean_desc = "_".join(words[:3])
    
    return f"{category}_{clean_desc}.jpg"

def generate_rename_suggestions(results):
    """Genera sugerencias de renombrado"""
    print("\n=== SUGERENCIAS DE RENOMBRADO ===")
    
    rename_plan = []
    
    for category, images in results.items():
        print(f"\n{category.upper()}:")
        
        for i, img in enumerate(images, 1):
            old_name = img["file"]
            new_name = img["suggested_name"]
            
            # Si el nombre sugerido es muy genérico, usar número
            if "unknown" in new_name or "error" in new_name:
                new_name = f"{category}_{i}.jpg"
            
            print(f"  {old_name} -> {new_name}")
            rename_plan.append({
                "old": os.path.join(category, old_name),
                "new": os.path.join(category, new_name)
            })
    
    # Guardar plan de renombrado
    plan_file = os.path.join(base_dir, "rename_plan.json")
    with open(plan_file, "w") as f:
        json.dump(rename_plan, f, indent=2)
    
    print(f"\nPlan de renombrado guardado en: {plan_file}")
    
    # Crear script de renombrado
    create_rename_script(rename_plan)

def create_rename_script(rename_plan):
    """Crea un script para renombrar las imágenes"""
    script_content = "#!/bin/bash\n# Script para renombrar imágenes basado en análisis de IA\n\n"
    script_content += f"cd \"{base_dir}\"\n\n"
    
    for item in rename_plan:
        old_path = item["old"]
        new_path = item["new"]
        
        # Verificar si el nuevo nombre ya existe
        script_content += f"if [ -f \"{new_path}\" ]; then\n"
        script_content += f"  echo \"Error: {new_path} ya existe\"\n"
        script_content += "else\n"
        script_content += f"  mv \"{old_path}\" \"{new_path}\"\n"
        script_content += f"  echo \"Renombrado: {old_path} -> {new_path}\"\n"
        script_content += "fi\n"
    
    script_file = os.path.join(base_dir, "rename_images.sh")
    with open(script_file, "w") as f:
        f.write(script_content)
    
    os.chmod(script_file, 0o755)
    print(f"Script de renombrado creado: {script_file}")
    print(f"\nPara ejecutar: cd \"{base_dir}\" && ./rename_images.sh")

if __name__ == "__main__":
    analyze_all_images()