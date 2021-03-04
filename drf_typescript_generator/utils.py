import importlib
import inspect

from rest_framework import serializers

from drf_typescript_generator.mappings import MAPPING


_DEFAULT_TYPE = 'any'

def _is_serializer(member):
    """ Returns whether the `member` is drf serializer class or not """
    return inspect.isclass(member) and serializers.BaseSerializer in inspect.getmro(member)


def _to_camelcase(s):
    parts = s.split('_')
    return parts[0] + ''.join([part.capitalize() for part in parts[1:]])


def _get_method_return_value_type(serializer, field_name, field):
    """
    For given method field looks for return type of corresponding
    method in type annotations.
    """
    method_name = field.method_name if field.method_name else f'get_{field_name}'
    method = getattr(serializer, method_name)
    method_signature = inspect.signature(method)
    return MAPPING.get(method_signature.return_annotation, _DEFAULT_TYPE)


def _get_typescript_name(field, field_name):
    typescript_field_name = _to_camelcase(field_name)
    if not field.required:
        typescript_field_name += '?'
    return typescript_field_name


def _get_typescript_type(field, field_name, serializer_instance):
    """
    Returns typescript type for given field based on global mapping.
    Supports also method fields, list like fields and nested serializers.
    Types derivation is not recursive (for nested serializer type
    {serializer.__name__} is returned). 
    If mapping for field type was not found default type is returned.
    """
    if type(field) == serializers.SerializerMethodField:
        return _get_method_return_value_type(serializer_instance, field_name, field)

    # core type is type of child in listfield / nested serializer with many=True
    is_list = hasattr(field, 'child')
    field_type = type(field.child) if is_list else type(field)

    if _is_serializer(field_type):
        typescript_type = field_type.__name__
    else:
        typescript_type = MAPPING.get(field_type, _DEFAULT_TYPE)

    return typescript_type + ('[]' if is_list else '')


def get_serializer_fields(serializer):
    """
    Determines a typescript type for every field in the serializer.
    Returns dictionary with keys being transformed field names to
    typescript names (including `?` if field is optional) and values
    being typescript types.
    """
    serializer_instance = serializer()
    fields = serializer_instance.get_fields()
    typescript_fields = {}
    for field_name, field in fields.items():
        typescript_field_name = _get_typescript_name(field, field_name)
        typescript_type = _get_typescript_type(field, field_name, serializer_instance)
        typescript_fields[typescript_field_name] = typescript_type

    return typescript_fields


def get_app_serializers(app_name):
    """ Returns all serializer classes found in {app_name}.serializers module """
    try:
        # TODO: dynamic name of serializers file?
        serializer_module = importlib.import_module('.serializers', package=app_name)
        return inspect.getmembers(serializer_module, _is_serializer)
    except ImportError:
        return []
