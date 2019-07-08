import requests
from flask import Flask, Response, __version__

app = Flask(__name__)

SEARCH_URL = 'https://www.immobilienscout24.de/Suche/S-2/Wohnung-Miete/Umkreissuche/Berlin_2dMitte_20_28Mitte_29/10178/228197/2512301/Alexanderplatz/-/3/1,50-/-/EURO--800,00'
DB_BUCKET = 'S58riYq8knK7KVPDseUMdD'
DB_KEY = 'seen_apartments'
DB_AUTH_KEY = 'ImmobilienScout24'
NOTIFICATION_URL = 'https://api.pushbullet.com/v2/pushes'
NOTIFICATION_AUTH_KEY = 'o.7KZCchEAcqwu9YCJwYm4pL0NeptbGl6P'


@app.route('/findplaces')
def find_new_places():
    seen_apartments = requests.get(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, '')).json()

    apartments = requests.post(SEARCH_URL).json()['searchResponseModel']['resultlist.resultlist']['resultlistEntries'][0]['resultlistEntry']

    unseen_apartments = []

    for apartment in apartments:
        if apartment['@id'] not in seen_apartments:
            unseen_apartments.append(apartment)
            seen_apartments.append(apartment['@id'])
    
    parsed_unseen_apartments = []

    for a in unseen_apartments:
        apartment = a['resultlist.realEstate']

        data = {
            'type': 'link',
            'title': f"New Apartment: {apartment['title']}",
            'body': f"Address: {apartment['address']['description']}\nSize: {apartment['livingSpace']}\nPrice (warm): {apartment['calculatedPrice']['value']} EUR",
            'url': f"https://www.immobilienscout24.de/expose/{a['@id']}"
        }

        parsed_unseen_apartments.append(data)

        requests.post(NOTIFICATION_URL, headers={'Access-Token': NOTIFICATION_AUTH_KEY}, json=data)

    requests.post(f'https://kvdb.io/{DB_BUCKET}/{DB_KEY}', auth=(DB_AUTH_KEY, ''), json=seen_apartments)

    return {
        'status' : 'SUCCESS',
        'unseen_apartments' : parsed_unseen_apartments
    }