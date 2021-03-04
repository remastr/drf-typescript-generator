import os
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

from drf_typescript_generator.utils import (
    _get_method_return_value_type, _get_typescript_name, _get_typescript_type, export_serializer,
    get_serializer_fields
)
from drf_typescript_generator.globals import DEFAULT_TYPE

from tests.utils import (
    ChoiceFieldTestSerializer, ListFieldTestSerializer, MethodOutputTestSerializer, 
    ModelTestSerializer, NestedSerializersTestSerializer, TypescriptNameTestSerializer
)

class BaseTest:
    def setup_method(self, test_method):
        self.serializer = self.serializer_class()
        self.fields = self.serializer.get_fields()


class TestRequired(BaseTest):
    serializer_class = TypescriptNameTestSerializer

    def test_typescript_required_name(self):
        ts_name = _get_typescript_name(self.fields['required_field'], 'required_field')
        assert ts_name == 'requiredField'

    def test_typescript_not_required_name(self):
        ts_name = _get_typescript_name(self.fields['not_required_field'], 'not_required_field')
        assert ts_name == 'notRequiredField?'


class TestMethodField(BaseTest):
    serializer_class = MethodOutputTestSerializer

    def test_method_unknown_return_type(self):
        ts_type, _ = _get_method_return_value_type(
            self.fields['unknown_output_type'], 'unknown_output_type', self.serializer
        )
        assert ts_type == DEFAULT_TYPE
        ts_type, _ = _get_method_return_value_type(
            self.fields['known_output_type'], 'known_output_type', self.serializer
        )
        assert ts_type == "number"

    def test_method_known_return_type(self):
        ts_type, _ = _get_method_return_value_type(
            self.fields['known_output_type'], 'known_output_type', self.serializer
        )
        assert ts_type == "number"


class TestChoiceField(BaseTest):
    serializer_class = ChoiceFieldTestSerializer

    def test_basic_choice_selection_fields(self):
        ts_type = _get_typescript_type(self.fields['choice_field_int'], 'choice_field_int', self.serializer)
        assert ts_type == '1 | 2 | 3'
        ts_type = _get_typescript_type(self.fields['choice_field_float'], 'choice_field_float', self.serializer)
        assert ts_type == '1.2 | 3.1'
        ts_type = _get_typescript_type(self.fields['choice_field_bool'], 'choice_field_bool', self.serializer)
        assert ts_type == 'true | false'
        ts_type = _get_typescript_type(self.fields['choice_field_str'], 'choice_field_str', self.serializer)
        assert ts_type == '"a" | "b"'

    def test_choice_selection_fields_with_empty_values(self):
        ts_type = _get_typescript_type(self.fields['choice_field_str_blank'], 'choice_field_str_blank', self.serializer)
        assert ts_type == '"a" | "b" | ""'
        ts_type = _get_typescript_type(self.fields['choice_field_int_null'], 'choice_field_int_null', self.serializer)
        assert ts_type == '1 | 2 | null'


class TestListField(BaseTest):
    serializer_class = ListFieldTestSerializer

    def test_basic_list_field_type(self):
        ts_type = _get_typescript_type(self.fields['lst'], 'lst', self.serializer)
        assert ts_type == 'number[]'

    def test_composite_list_field_type(self):
        ts_type = _get_typescript_type(self.fields['composite_lst'], 'composite_lst', self.serializer)
        assert ts_type == '(number | null)[]'

    def test_multiple_choice_field(self):
        ts_type = _get_typescript_type(self.fields['multichoice'], 'multichoice', self.serializer)
        assert ts_type == '(1 | 2 | 3)[]'


def test_model_serializer():
    fields = get_serializer_fields(ModelTestSerializer)
    options = {
        'format': 'type',
        'semicolons': False,
        'tabs': None,
        'spaces': 2
    }
    ts_serializer = export_serializer('ModelTestSerializer', fields, options)
    assert ' '.join(ts_serializer.split()).strip() == ' '.join(
        """
        export type ModelTestSerializer = {
            field1?: string
            field2: number
            field3: number
        }
        """.split()
    ).strip()


class TestNestedSerializers(BaseTest):
    serializer_class = NestedSerializersTestSerializer

    def test_single_object_nested_serializer(self):
        ts_type = _get_typescript_type(self.fields['model'], 'model', self.serializer)
        assert ts_type == 'ModelTestSerializer'

    def test_many_objects_nested_serializer(self):
        ts_type = _get_typescript_type(self.fields['models'], 'models', self.serializer)
        assert ts_type == 'ModelTestSerializer[]'

    def test_nullable_many_objects_nested_serializer(self):
        ts_type = _get_typescript_type(self.fields['models_nullable'], 'models_nullable', self.serializer)
        assert ts_type == '(ModelTestSerializer | null)[]'
