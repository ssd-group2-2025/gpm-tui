import dataclasses

import typeguard
from typeguard import check_type


def validate_dataclass(dataclass_instance):
    for field in dataclasses.fields(dataclass_instance):
        check_type(
            value=getattr(dataclass_instance, field.name),
            expected_type=field.type,
            forward_ref_policy=typeguard.config.forward_ref_policy,
            typecheck_fail_callback=typeguard.config.typecheck_fail_callback,
            collection_check_strategy=typeguard.config.collection_check_strategy
        )
