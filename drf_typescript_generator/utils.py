import importlib
import inspect
import os
from collections import OrderedDict

from rest_framework import routers, serializers

from drf_typescript_generator.globals import (
    CHOICES_TRANSFORM_FUNCTIONS_BY_TYPE, DEFAULT_TYPE, MAPPING, SPECIAL_FIELD_TYPES
)


def _is_serializer_class(member):
    """ Returns whether the `member` is drf serializer class or not """
    return inspect.isclass(member) and serializers.BaseSerializer in inspect.getmro(member)


def _is_router_instance(member):
    """ Returns whether the `member` is drf router or not """
    return not inspect.isclass(member) and routers.BaseRouter in inspect.getmro(member.__class__)


def _to_camelcase(s):
    parts = s.split('_')
    return parts[0] + ''.join([part.capitalize() for part in parts[1:]])


def _check_for_nullable(field, typescript_type):
    if field.allow_null:
        typescript_type += ' | null'
    return typescript_type


def _get_project_name():
    return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]


def _get_typescript_name(field, field_name):
    typescript_field_name = _to_camelcase(field_name)
    if not field.read_only and not field.required:
        typescript_field_name += '?'
    return typescript_field_name


def _get_method_return_value_type(field, field_name, serializer_instance):
    """
    For given method field function looks for return type of corresponding
    method in type annotations.
    """
    method_name = field.method_name if field.method_name else f'get_{field_name}'
    method = getattr(serializer_instance, method_name)
    method_signature = inspect.signature(method)
    return MAPPING.get(method_signature.return_annotation, DEFAULT_TYPE), False


def _get_choice_selection_fields_type(field):
    """
    Returns composite typescript type for choice selection field
    by enumerating its choices. Also takes into account the
    allow_blank argument.
    """
    def transform_choice(v):
        return str(CHOICES_TRANSFORM_FUNCTIONS_BY_TYPE[type(v)](v))

    typescript_type = ' | '.join([transform_choice(choice) for choice in field.choices.keys()])
    is_list = type(field) == serializers.MultipleChoiceField
    if field.allow_blank:
        typescript_type += ' | ""'

    return typescript_type, is_list


def _handle_special_field_type(field, field_name, serializer_instance):
    """
    This function is used for fields that require custom logic for
    deriving its type. Custom function based on field type is called
    in sake of finding typescript type for this field.
    """
    if type(field) == serializers.SerializerMethodField:
        return _get_method_return_value_type(field, field_name, serializer_instance)
    elif type(field) in [serializers.ChoiceField, serializers.MultipleChoiceField]:
        return _get_choice_selection_fields_type(field)
    else:
        raise NotImplementedError(
            f'Handling of {type(field).__name__} special field is not implemented'
        )


def _handle_nonspecial_field_type(field):
    """
    Function determines typescript type for field that does not
    require special logic to derive its type e.g. field in
    String fields category, Numeric fields category, ...
    """
    # core type is type of child in listfield / nested serializer with many=True
    is_list = hasattr(field, 'child')
    field_type = type(field.child) if is_list else type(field)

    if _is_serializer_class(field_type):
        typescript_type = field_type.__name__
    else:
        typescript_type = MAPPING.get(field_type, DEFAULT_TYPE)
    return typescript_type, is_list


def _get_typescript_type(field, field_name, serializer_instance):
    """
    Returns typescript type for given field based on global mapping.
    Supports also method fields, list like fields and nested serializers.
    Types derivation is not recursive (for nested serializer type
    {serializer.__name__} is returned).
    If mapping for field type was not found default type is returned.
    """
    if type(field) in SPECIAL_FIELD_TYPES:
        typescript_type, is_list = _handle_special_field_type(field, field_name, serializer_instance)
    else:
        typescript_type, is_list = _handle_nonspecial_field_type(field)

    typescript_type = _check_for_nullable(field, typescript_type)

    if is_list and '|' in typescript_type:
        # composite type array needs to be in parenthesis e.g. (number | null)[]
        typescript_type = f'({typescript_type})'

    return typescript_type + ('[]' if is_list else '')


def get_nested_serializers(serializer):
    """
    Finds nested serializers in given serializer. Returns
    ordered dictionary with keys being name of the nested
    serializers and values nested serializer classes.
    """
    serializer_instance = serializer()
    fields = serializer_instance.get_fields()
    nested_serializers = {}
    for field in fields.values():
        is_list = hasattr(field, 'child')
        field_type = type(field.child) if is_list else type(field)
        if _is_serializer_class(field_type):
            nested_serializers[field_type.__name__] = field_type

    return OrderedDict(sorted(nested_serializers.items()))


def get_serializer_fields(serializer):
    """
    Determines a typescript type for every field in the serializer.
    Returns ordered dictionary with keys being transformed field names to
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

    return OrderedDict(sorted(typescript_fields.items()))


def get_app_routers(app_name):
    """ Returns all routers found in {app_name}.urls module """
    try:
        urls_module = importlib.import_module('.urls', package=app_name)
        return inspect.getmembers(urls_module, _is_router_instance)
    except ImportError:
        return []


def get_project_routers():
    """ Returns all routers found in project urls module """
    project_name = _get_project_name()
    return get_app_routers(project_name)


def get_module_serializers(module):
    """ Returns all serializer classes found in given module """
    try:
        urls_module = importlib.import_module(module)
        return inspect.getmembers(urls_module, _is_serializer_class)
    except ImportError:
        return []


def export_serializer(serializer_name, fields, options):
    def format_field(field, indent):
        formatted = f'{indent}{field[0]}: {field[1]}'
        if options['semicolons']:
            formatted += ';'
        return formatted

    indent = '\t' * options['tabs'] if options['tabs'] is not None else ' ' * options['spaces']
    attributes = '\n'.join([format_field(field, indent) for field in fields.items()])

    if options['format'] == 'type':
        template = 'export type {} = {{\n{}\n}}\n\n'
    else:
        template = 'export interface {} {{\n{}\n}}\n\n'

    return template.format(serializer_name, attributes)
