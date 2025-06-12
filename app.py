import time
from flask import Flask, render_template, request, jsonify
import requests
from config import GOOGLE_API_KEY

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
        'fields': 'name,formatted_address,formatted_phone_number,geometry/location,types',
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
                    phone = info.get('formatted_phone_number', '')
                    results.append({
                        'name': name,
                        'phone': phone,
                        'address': address,
                        'category': category,
                        'city': city,
                        'state': state,
                        'lat': location.get('lat'),
                        'lng': location.get('lng'),
                        'place_id': place_id
                    })
                pagetoken = data.get('next_page_token')
                if pagetoken and pages < 2:
                    pages += 1
                    time.sleep(2)
                    continue
                break
            time.sleep(1)
    return jsonify(results)
if __name__ == '__main__':
    app.run(debug=True)
