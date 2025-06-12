# Google Maps Search App

This project provides a simple Flask application that searches Google Places in multiple cities for multiple keywords and displays the results on an interactive Google Map. Searches rely on the Geocoding API together with Places **Nearby Search** and pagination to gather up to 60 businesses per city and keyword.

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


## Result actions

Each search result includes the business phone number, address and place ID. In the results table you can:
- **Ver en Google Maps**: open the location in a new tab.
- **Eliminar**: remove the row from the list without reloading.
- **Copiar**: copy the name, address and phone number to the clipboard.

