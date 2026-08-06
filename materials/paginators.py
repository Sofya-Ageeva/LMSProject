from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """Пагинация для курсов"""
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 10


class LessonPagination(PageNumberPagination):
    """Пагинация для уроков"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20
