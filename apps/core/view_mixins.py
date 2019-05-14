from django.core.exceptions import PermissionDenied


class GroupRequiredMixin(object):
    """
    blatantly stolen from this gist: https://gist.github.com/ceolson01/206139a093b3617155a6

        group_required - list of strings, required param
    """

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            user_groups = [group for group in request.user.groups.values_list('name', flat=True)]
            if len(set(user_groups).intersection(self.group_required)) <= 0:
                raise PermissionDenied
        return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)
