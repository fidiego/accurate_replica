from uuid import uuid4

from django.contrib.auth.models import Group
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from django.apps import apps


class BaseModelMixin(models.Model):
    """all of our models inherit from this mixin"""

    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModelMixin(models.Model):
    deleted_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class EntityRelatedModelMixin(models.Model):
    """
    Models that can be related to entities should inherit from this Mixin. The mixin
    rovides a denormalized way to relate entities to each other without requiring
    deep joins etc. This is a small, forward-looking optimization.

    If, in the future, we wanted to split tags and notes off from this app, it would
    be easy to to so given this structure.


    ENTITY_TYPES can be provided to validate new instantiations. It takes a list of
    app_label.ModelName formatted strings.

    n.b. Careful with any models that have the same name across different apps because
    this is not written to handle that case.
    """

    ENTITY_TYPES = []  #
    entity_type = models.CharField(max_length=32)
    entity_uuid = models.CharField(max_length=36)

    class Meta:
        abstract = True

    def entity(self):
        return f"{self.entity_type}:{self.entity_uuid}"

    @classmethod
    def validate_entity(cls, entity, uuid):
        if not cls.ENTITY_TYPES:
            return

        entity_map = {
            model.strip().lower(): f"{app_label}.{model}"
            for app_label, model in [t.split(".") for t in cls.ENTITY_TYPES]
        }

        try:
            model = get_model(entity_map[entity])
            return True
        except LookupError as e:
            logger.exception(e)
            return False


class UserGroupMembershipModelMixin(models.Model):
    class Meta:
        abstract = True

    def add_to_user_group(self):
        group = Group.objects.get(name=self.USER_GROUP)
        group.user_set.add(self.user)
        group.save()
