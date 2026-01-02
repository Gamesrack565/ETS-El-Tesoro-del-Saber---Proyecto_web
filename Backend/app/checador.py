import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: No se encontró la API KEY en .env")
else:
    print(f"✅ API Key encontrada: {api_key[:5]}...")

    try:
        genai.configure(api_key=api_key)
        print("\n🔎 Buscando modelos disponibles para tu cuenta...")
        
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
                found = True
        
        if not found:
            print("\n⚠️ No se encontraron modelos compatibles con 'generateContent'.")
            print("   Posible causa: Tu API Key no tiene permisos o es inválida.")
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")