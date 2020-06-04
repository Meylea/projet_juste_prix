# -- coding: utf-8 --
import requests
import json
import random
from flask import Flask, render_template, request, session, url_for
from timeit import default_timer as timer

app = Flask(__name__)
app.secret_key = '\xec\xdf\xa1\x19\xf7\x82\xb3\x81\x1b\xbeb\n"\x99\xc6.'


@app.route('/', methods=['GET', 'POST'])
def init_game():
    if request.method == 'GET':
        url = 'https://api.cdiscount.com/OpenApi/json/Search'
        payload = {
            "ApiKey": "ce1e0c0e-1591-41b4-bf55-ffb0b1264900",
            "SearchRequest": {
                "Keyword": "tablette",
                "SortBy": "",
                "Pagination": {"ItemsPerPage": 10, "PageNumber": random.randrange(0, 9)},
                "Filters": {"Price": {"Min": 0, "Max": 0}, "Navigation": "", "IncludeMarketPlace": False, "Condition": None}
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
            session['start'] = timer()
            session['answers'] = []
        answer = request.form['answer']
        answer = answer.replace(',', '.')
        try:
            answer = float(answer)
        except ValueError:
            return render_template(
                'index.html',
                error="Veuillez entrer une valeur numérique avec maximum deux chiffres derrière la virgule !",
                product=session['product']
            )
        message = None
        if answer == session['product']['price']:
            stop = timer()
            time = stop - session['start']
            message = f'Vous avez gagné en {time} secondes !'
        if answer > session['product']['price']:
            message = 'Plus bas !'
        if answer < session['product']['price']:
            message = 'Plus haut !'
        session['answers'].append("answer")
        return render_template(
            'index.html',
            product=session['product'],
            message=message,
            answers=session['answers']
        )


if __name__ == '__main__':
    app.run(debug=True)
