from flask import Flask, render_template, session, redirect, url_for, request
import webbrowser
import threading
import os

app = Flask(__name__)
app.secret_key = '101'

services = [
    {'id': 1, 'name': 'Установка бытовой техники', 'price': 3000, 'category': 'бытовая техника'},
    {'id': 2, 'name': 'Сантехнические работы', 'price': 4500, 'category': 'сантехника'},
    {'id': 3, 'name': 'Электромонтажные работы', 'price': 3500, 'category': 'электрика'},
    {'id': 4, 'name': 'Сборка мебели', 'price': 2500, 'category': 'мебель'},
    {'id': 5, 'name': 'Ремонт квартир под ключ', 'price': 15000, 'category': 'ремонт'},
    {'id': 6, 'name': 'Мелкий бытовой ремонт', 'price': 2000, 'category': 'ремонт'}
]


def load_reviews_from_file():
    try:
        with open('feedback.txt', 'r', encoding='utf-8') as file:
            content = file.read()
            namespace = {}
            exec(content, namespace)
            return namespace.get('reviews', [])
    except Exception as e:
        print(f"Ошибка при загрузке отзывов: {e}")
        return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/services')
def show_services():
    categories = list(set(service['category'] for service in services))
    return render_template('services.html', services=services, categories=categories)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    service_id = int(request.form['service_id'])
    quantity = int(request.form.get('quantity', 1))
    service = next(s for s in services if s['id'] == service_id)

    if 'cart' not in session:
        session['cart'] = []

    found = False
    for item in session['cart']:
        if item['service']['id'] == service_id:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        session['cart'].append({
            'service': service,
            'quantity': quantity
        })

    session.modified = True
    return redirect(url_for('show_services'))


@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    total = sum(item['service']['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)


@app.route('/remove_from_cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        del cart[index]
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('show_cart'))


@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        return redirect(url_for('show_services'))

    session.pop('cart', None)
    return render_template('order_success.html')


@app.route('/reviews')
def show_reviews():
    reviews = load_reviews_from_file()
    return render_template('reviews.html', reviews=reviews)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(0.1, open_browser).start()
    app.run(debug=True)