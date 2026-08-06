import stripe
from django.conf import settings
from users.models import Payment


def create_stripe_product(course):
    """Создание продукта в Stripe"""
    try:
        product = stripe.Product.create(
            name=course.name,
            description=course.description or "",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания продукта: {str(e)}")


def create_stripe_price(product_id, amount):
    """Создание цены в Stripe"""
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # Цена в копейках!
            currency="rub",
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания цены: {str(e)}")


def create_checkout_session(price_id, success_url, cancel_url):
    """Создание сессии для оплаты в Stripe"""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка создания сессии: {str(e)}")
