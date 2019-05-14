from rest_framework.pagination import LimitOffsetPagination


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    limit_query_param = "limit"
    offset_query_param = "offset"
    default_limit = 100
    max_limit = 2500
