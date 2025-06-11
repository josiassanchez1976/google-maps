import time
from flask import Flask, render_template, request, jsonify
import requests
from config import GOOGLE_API_KEY
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)

FILTER_WORDS = ["home depot", "lowe", "abc supply"]

@app.route('/')
def index():
    return render_template('index.html', google_api_key=GOOGLE_API_KEY)


def geocode_city(city, state):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': f'{city},{state}' if state else city,
        'key': GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data.get('results'):
        loc = data['results'][0]['geometry']['location']
        return loc.get('lat'), loc.get('lng')
    return None, None


def call_nearby_search(keyword, lat, lng, pagetoken=None):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'keyword': keyword,
        'location': f'{lat},{lng}',
        'radius': 50000,
        'key': GOOGLE_API_KEY
    }
    if pagetoken:
        params['pagetoken'] = pagetoken
    resp = requests.get(url, params=params)
    return resp.json()


def call_place_details(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,geometry/location,types',
        'key': GOOGLE_API_KEY
    }
    resp = requests.get(url, params=params)
    return resp.json()


@app.route('/search', methods=['POST'])
def search():
    cities = request.form.get('cities', '')
    keywords = request.form.get('keywords', '')
    state = request.form.get('state', '')

    city_list = [c.strip() for c in cities.split(',') if c.strip()]
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]

    results = []
    seen = set()

    for city in city_list:
        lat, lng = geocode_city(city, state)
        if lat is None or lng is None:
            continue
        for keyword in keyword_list:
            pagetoken = None
            pages = 0
            while True:
                data = call_nearby_search(keyword, lat, lng, pagetoken)
                for place in data.get('results', []):
                    place_id = place.get('place_id')
                    if not place_id or place_id in seen:
                        continue
                    seen.add(place_id)
                    details = call_place_details(place_id)
                    info = details.get('result', {})
                    name = info.get('name', place.get('name', ''))
                    if any(bad in name.lower() for bad in FILTER_WORDS):
                        continue
                    types = info.get('types', [])
                    category = types[0] if types else ''
                    location = info.get('geometry', {}).get('location', {})
                    address = info.get('formatted_address', place.get('vicinity', ''))
                    results.append({
                        'name': name,
                        'address': address,
                        'category': category,
                        'city': city,
                        'state': state,
                        'lat': location.get('lat'),
                        'lng': location.get('lng'),
                        'place_id': place_id,
                        'categoria_real': ''
                    })
                pagetoken = data.get('next_page_token')
                if pagetoken and pages < 2:
                    pages += 1
                    time.sleep(2)
                    continue
                break
            time.sleep(1)
    return jsonify(results)


@app.route('/get_real_categories', methods=['POST'])
def get_real_categories():
    data = request.get_json(force=True)
    results = data.get('results', [])

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)

    for item in results:
        place_id = item.get('place_id')
        if not place_id:
            continue
        url = f'https://www.google.com/maps/place/?q=place_id:{place_id}'
        try:
            driver.get(url)
            try:
                elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button[jsaction="pane.wfvdle63.category"]')
                    )
                )
                item['categoria_real'] = elem.text.strip()
            except TimeoutException:
                print(f"[ERROR] Timeout retrieving category for {place_id}")
                item['categoria_real'] = ''
        except Exception as e:
            print(f"[ERROR] {place_id}: {e}")
            item['categoria_real'] = ''
        time.sleep(1)

    driver.quit()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
