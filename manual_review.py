import json
import sys
import time
from selenium import webdriver

from config import GOOGLE_API_KEY  # not strictly needed but ensures config is loaded


def review(results):
    options = webdriver.ChromeOptions()
    # visible browser (no headless)
    driver = webdriver.Chrome(options=options)
    accepted = []
    try:
        for item in results:
            place_id = item.get('place_id')
            if not place_id:
                continue
            url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            driver.get(url)
            print(f"Revisando: {item.get('name')} - {item.get('address')}")
            decision = ''
            while decision not in ('a', 'd'):
                decision = input("[a] agregar / [d] descartar: ").strip().lower()
            if decision == 'a':
                accepted.append(item)
    finally:
        driver.quit()
    with open('resultados_filtrados.json', 'w', encoding='utf-8') as f:
        json.dump(accepted, f, indent=2, ensure_ascii=False)
    print(f"Guardados {len(accepted)} resultados en resultados_filtrados.json")


def main():
    if len(sys.argv) < 2:
        print("Uso: python manual_review.py <archivo_resultados.json>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        results = json.load(f)
    review(results)


if __name__ == '__main__':
    main()
