from accompaniment.models import Responder
from operators.models import Operator
from attorneys.models import Attorney


MODEL_MAPPING = {"responder": Responder, "operator": Operator, "attorney": Attorney}


def get_phone_number(entity: str) -> str:
    """
    takes entity string and returns entitie's phone number

    format: responder:9a89d16f-9617-44dc-945a-22b4ed6b4055
    """
    type_, uuid = entity.split(":")
    model = MODEL_MAPPING.get(type_)
    if not model:
        return
    return model.user.phone_number
