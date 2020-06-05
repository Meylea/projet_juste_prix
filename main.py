# -- coding: utf-8 --
import re

import requests
import json
import random
from flask import Flask, render_template, request, session
from timeit import default_timer as timer

app = Flask(__name__)
app.secret_key = '\xec\xdf\xa1\x19\xf7\x82\xb3\x81\x1b\xbeb\n"\x99\xc6.'
answers = []


@app.route('/', methods=['GET', 'POST'])
def init_game():
    global answers
    if request.method == 'GET':
        url = 'https://api.cdiscount.com/OpenApi/json/Search'
        payload = {
            "ApiKey": "ce1e0c0e-1591-41b4-bf55-ffb0b1264900",
            "SearchRequest": {
                "Keyword": "electronique",
                "SortBy": "",
                "Pagination": {"ItemsPerPage": 10, "PageNumber": random.randrange(0, 9)},
                "Filters": {
                    "Price": {"Min": 0, "Max": 0},
                    "Navigation": "",
                    "IncludeMarketPlace": False,
                    "Condition": None}
            }
        }
        r = requests.post(url, data=json.dumps(payload))
        data = json.loads(r.text)
        product_data = data['Products'][random.randrange(0, len(data['Products']))]
        image_link = product_data['MainImageUrl']
        price = round(float(product_data['BestOffer']['SalePrice']), 2)
        name = product_data['Name']
        session['product'] = {'image': image_link, 'price': price, 'name': name}
        session['first_guess'] = True
        return render_template(
            'index.html',
            product=session['product']
        )

    else:
        if session['first_guess']:
            session['first_guess'] = False
            session['game_ended'] = False
            session['start'] = timer()
            answers = []
        answer = request.form['answer']
        answer = answer.replace(',', '.')
        try:
            assert re.match('^[0-9]+[.]?[0-9]{,2}$', answer)
            answer = float(answer)
        except (AssertionError, ValueError):
            return render_template(
                'index.html',
                error="Veuillez entrer une valeur numérique postitive avec maximum deux chiffres derrière la virgule !",
                product=session['product'],
                answers=answers
            )
        message = None
        stop = timer()
        time = round(stop - session['start'], 3)
        if answer == session['product']['price']:
            message = f'Vous avez gagné en {time} secondes !'
            session['game_ended'] = True
        if answer > session['product']['price']:
            message = 'Plus bas !'
        if answer < session['product']['price']:
            message = 'Plus haut !'
        answers.insert(0, {'price': round(answer, 2), 'time': time})
        return render_template(
            'index.html',
            product=session['product'],
            message=message,
            answers=answers,
            game_ended=session['game_ended']
        )


if __name__ == '__main__':
    app.run(debug=True)
