"""
src: https://stackoverflow.com/questions/18016543/django-filter-in-lookup
src: https://github.com/carltongibson/django-filter/issues/137#issuecomment-77697870
"""
import logging
import uuid

from django.db.models import Q
from django_filters import Filter
from django_filters.fields import Lookup


class ListFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", "")
        self._label = self.name
        self.extra = {}
        super(*args, **kwargs)

    def sanitize(self, value_list):
        """
        remove empty items in case of ?number=1,,2
        """
        return [v for v in value_list if v.strip() != u""]

    def customize(self, value):
        return value

    def filter(self, qs, value: str):
        if not value:
            logging.warning("List Filter with no value")
            return qs

        value_list = list(map(self.customize, self.sanitize(value.split(u","))))

        f = Q()
        for v in value_list:
            kwargs = {self.name: v}
            f = f | Q(**kwargs)

        return qs.filter(f)


class UUIDListFilter(ListFilter):
    def customize(self, value):
        return uuid.UUID(value)
