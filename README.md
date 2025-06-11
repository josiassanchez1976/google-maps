# Google Maps Search App

This project provides a simple Flask application that searches Google Places in multiple cities for multiple keywords and displays the results on an interactive Google Map. Searches now rely on the Geocoding API together with Places **Nearby Search** and pagination to gather up to 60 businesses per city and keyword.

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

The server will be available at `http://localhost:5000/`.

## Configuration

The Google API key is stored in `config.py` as `GOOGLE_API_KEY`. Update it with your own key if needed.

## Real Category Extraction

After performing a search, use the **Obtener categorías reales** button to fetch
the category displayed on Google Maps for each result. This step runs Selenium
in headless Chrome, so ensure Chrome/ChromeDriver are installed.

## Manual visual review

Export your search results as JSON and then run:

```bash
python manual_review.py results.json
```

This script opens Chrome (visible) one location at a time using Selenium so you
can decide whether to **agregar** (a) or **descartar** (d) each result. Accepted
places are saved to `resultados_filtrados.json`.
