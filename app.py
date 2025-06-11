import time
from flask import Flask, render_template, request, jsonify
import requests
from config import GOOGLE_API_KEY

app = Flask(__name__)

FILTER_WORDS = ["home depot", "lowe", "abc supply"]

@app.route('/')
def index():
    return render_template('index.html', google_api_key=GOOGLE_API_KEY)


def call_text_search(query):
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': query,
        'key': GOOGLE_API_KEY
    }
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
        for keyword in keyword_list:
            query = f"{keyword} in {city}"
            if state:
                query += f" {state}"
            data = call_text_search(query)
            for place in data.get('results', []):
                name = place.get('name', '')
                if any(bad in name.lower() for bad in FILTER_WORDS):
                    continue
                identifier = (name.lower(), city.lower())
                if identifier in seen:
                    continue
                seen.add(identifier)
                place_id = place.get('place_id')
                details = call_place_details(place_id)
                info = details.get('result', {})
                types = info.get('types', [])
                category = types[0] if types else ''
                location = info.get('geometry', {}).get('location', {})
                lat = location.get('lat')
                lng = location.get('lng')
                address = info.get('formatted_address', '')
                results.append({
                    'name': name,
                    'address': address,
                    'category': category,
                    'city': city,
                    'state': state,
                    'lat': lat,
                    'lng': lng
                })
            time.sleep(1)  # rudimentary throttling
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
