from .db_session import *
from .items import *
from flask import Flask, render_template, request, url_for, make_response, redirect
from .coupons import COUPONS


global_init('db/shop.sqlite')
db_sess = create_session()


def get_categories():
    global db_sess
    categories = db_sess.query(Category).all()
    return categories


def get_items():
    global db_sess
    items = db_sess.query(Item).all()
    return items


def get_items_by_category(category):
    global db_sess
    category_id = db_sess.query(Category).filter(Category.name == category).first().id
    items_by_category = db_sess.query(Item).filter(Item.category_id == category_id).all()
    return items_by_category


def get_category_image(category):
    return url_for('static', filename=f'images/categories/{category.image}')


def get_item_image(item):
    return url_for('static', filename=f'images/items/{item.image}')


def get_price(item):
    return get_nice_price(item.price)


def get_nice_price(price):
    price = format(price, '.2f')
    a = list()
    if float(price) >= 1000:
        for i in range(len(price[:-7]), -1, -3):
            a.append(i)
        value = list(price)
        for i in a:
            value.insert(i + 1, " ")
        return ''.join(value)
    else:
        return price


def get_item_object(item):
    global db_sess
    return db_sess.query(Item).filter(Item.name == item).first()


def get_items_from_cookies(cookie):
    global db_sess
    objects = cookie.split(';')
    items = list()
    for obj in objects[:-1]:
        item = db_sess.query(Item).filter(Item.id == obj).first()
        items.append(item)
    return items


def get_amount_cart(cart):
    sum = 0
    for i in cart:
        sum += i.price
    return sum


def get_cart_size():
    return len(request.cookies.get('cart').split(';')) - 1


def get_total_cart(cart):
    amount = get_amount_cart(cart)
    discount = get_discount()
    total = amount - discount
    if total < 0:
        total = 0
    return total


def get_discount():
    global COUPONS
    discount = COUPONS.get(request.cookies.get('discount'))
    if discount == None:
        return 0
    return discount


def get_cart_for_checkout():
    items = get_items_from_cookies(request.cookies.get('cart'))
    price = list(map(lambda x: f'{x.name} - {get_price(x)} RUB', items))
    result = ['Вы купили:']
    for i in price:
        result.append(i)
    result.append(f'Общей стоимостью: {get_nice_price(get_total_cart(items))} RUB (скидка - {get_discount()} RUB)')
    return result


def get_request():
    return request.form['search']


def get_items_via_search(text):
    global db_sess
    return db_sess.query(Item).filter(Item.name.like(f"%{text}%")).all()