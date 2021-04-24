from data.functions import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/init_cart')
def initilization_cart():
    res = make_response(redirect('/'))
    res.set_cookie('cart', '0', max_age=60*60*24)
    return res


@app.route('/init_discount')
def initilization_discount():
    res = make_response(redirect('/'))
    res.set_cookie('discount', '0', max_age=60*60*24)
    return res


@app.route('/')
def index():
    if not request.cookies.get('cart'):
        return redirect('/init_cart')
    elif not request.cookies.get('discount'):
        return redirect('/init_discount')
    return render_template('index.html', categories=get_categories(), len=lambda x: len(x),
                            get_category_image=get_category_image,
                            get_items_by_category=get_items_by_category,
                            cart_size=get_cart_size(), req=get_request)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        res = make_response(redirect('/cart'))
        if request.form['coupon'] != '':
            res.set_cookie('discount', request.form['coupon'], max_age=60*60*24)
        return res

    elif request.method == 'GET':
        if not request.cookies.get('cart'):
            return redirect('/init_cart')
        elif not request.cookies.get('discount'):
            return redirect('/init_discount')

        cookie = request.cookies.get('cart')
        if cookie != '0':
            items = get_items_from_cookies(cookie)
        else:
            items = list()
        global db_sess
        return render_template('cart.html', cart=items, cart_size=get_cart_size(),
                                get_item_image=get_item_image, get_price=get_price,
                                category=lambda x: db_sess.query(Category).filter(Category.id == x).first().name,
                                int=lambda x:int(x), get_amount_cart=get_amount_cart, get_nice_price=get_nice_price,
                                get_total_cart=get_total_cart, get_discount=get_discount,
                                discount=request.cookies.get('discount'), get_cart_for_checkout=get_cart_for_checkout)


@app.route('/category/<category>')
def category_items(category):
    if not request.cookies.get('cart'):
        return redirect('/init_cart')
    elif not request.cookies.get('discount'):
        return redirect('/init_discount')
    return render_template('items_by_category.html', category=category, get_price=get_price,
                            items=get_items_by_category(category), len=lambda x: len(x),
                            get_item_image=get_item_image,
                            cart_size=get_cart_size())


@app.route('/category/<category>/item/<item>')
def product_page(category, item):
    if not request.cookies.get('cart'):
        return redirect('/init_cart')
    elif not request.cookies.get('discount'):
        return redirect('/init_discount')
    return render_template('item.html', item=get_item_object(item), category=category,
                            get_item_image=get_item_image, get_price=get_price,
                            cart_size=get_cart_size())


@app.route('/checkout')
def checkout():
    res = make_response(render_template('checkout.html', get_cart_for_checkout=get_cart_for_checkout(), cart_size=0))
    res.set_cookie('cart', '0', max_age=60*60*24)
    return res


@app.route('/search', methods=['POST'])
def search_post():
    return redirect(f"/search/{request.form['search']}")


@app.route('/search/<text>')
def search(text):
    return render_template('items_by_category.html', category=f"Результаты по запросу: {text}", get_price=get_price,
                           items=get_items_via_search(text), len=lambda x: len(x),
                           get_item_image=get_item_image,
                           cart_size=get_cart_size())


@app.route('/remove/<item>')
def remove(item):
    res = make_response(redirect('/cart'))
    items = request.cookies.get('cart').split(';')[:-1]
    if len(items) == 1:
        res.set_cookie('cart', '0', max_age=60*60*24)
    else:
        del items[int(item) - 1]
        res.set_cookie('cart', ';'.join(items) + ';', max_age=60*60*24)
    return res


@app.route('/add/<item>')
def add(item):
    if request.cookies.get('cart') == '0':
        cart_items = f'{item};'
    else:
        cart_items = request.cookies.get('cart') + f'{item};'
    res = make_response(redirect('/cart'))
    res.set_cookie('cart', cart_items, max_age=60 * 60 * 24)
    return res


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
