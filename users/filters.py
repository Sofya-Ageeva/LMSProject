from django_filters import rest_framework as filters
from .models import Payment


class PaymentFilter(filters.FilterSet):
    """Фильтр для модели Payment"""

    paid_course = filters.NumberFilter(field_name='paid_course__id')

    paid_lesson = filters.NumberFilter(field_name='paid_lesson__id')

    payment_method = filters.ChoiceFilter(choices=Payment.PaymentMethod.choices)

    ordering = filters.OrderingFilter(
        fields=(
            ('payment_date', 'payment_date'),
        )
    )

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'payment_method']