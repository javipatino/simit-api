import asyncio
import sys
import re
import nest_asyncio
nest_asyncio.apply()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

@app.get("/consultar/{numero_documento}")
def consultar_simit(numero_documento: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://www.fcm.org.co/simit/#/home-public")
        page.wait_for_timeout(5000)
        
        try:
            page.click(".close", timeout=3000)
        except:
            pass
        
        page.fill("#txtBusqueda", numero_documento)
        page.wait_for_timeout(1000)
        page.keyboard.press("Enter")
        page.wait_for_timeout(6000)
        
        texto = page.inner_text("body")
        browser.close()
        
        # Extraer datos relevantes
        comparendos = re.search(r"Comparendos:\s*(\d+)", texto)
        multas = re.search(r"Multas:\s*(\d+)", texto)
        total = re.search(r"Total:\s*\$\s*([\d.,]+)", texto)
        paz_salvo = "Sí" if "No tienes comparendos ni multas" in texto else "No"
        
        return {
            "documento": numero_documento,
            "paz_salvo": paz_salvo,
            "comparendos": comparendos.group(1) if comparendos else "N/A",
            "multas": multas.group(1) if multas else "N/A",
            "total_deuda": total.group(1) if total else "N/A"
        }