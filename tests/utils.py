import django
from django.db import models
from rest_framework import serializers

django.setup()


class TypescriptNameTestSerializer(serializers.Serializer):
    required_field = serializers.CharField(max_length=255)
    not_required_field = serializers.CharField(max_length=255, required=False)


class MethodOutputTestSerializer(serializers.Serializer):
    unknown_output_type = serializers.SerializerMethodField()
    known_output_type = serializers.SerializerMethodField()

    def get_unknown_output_type(self, obj):
        pass

    def get_known_output_type(self, obj) -> int:
        return 1


class ChoiceFieldTestSerializer(serializers.Serializer):
    choice_field_int = serializers.ChoiceField(choices=[1, 2, 3])
    choice_field_float = serializers.ChoiceField(choices=[1.2, 3.1])
    choice_field_bool = serializers.ChoiceField(choices=[True, False])
    choice_field_str = serializers.ChoiceField(choices=["a", "b"])
    choice_field_str_blank = serializers.ChoiceField(choices=["a", "b"], allow_blank=True)
    choice_field_int_null = serializers.ChoiceField(choices=[1, 2], allow_null=True)


class ListFieldTestSerializer(serializers.Serializer):
    lst = serializers.ListField(child=serializers.IntegerField())
    composite_lst = serializers.ListField(child=serializers.IntegerField(), allow_null=True)
    multichoice = serializers.MultipleChoiceField(choices=[1, 2, 3])


class Model(models.Model):
    field1 = models.CharField(max_length=255, blank=True)
    field2 = models.IntegerField()

    class Meta:
        app_label = 'tests'


class ModelTestSerializer(serializers.ModelSerializer):
    field3 = serializers.IntegerField()

    class Meta:
        model = Model
        fields = ['field1', 'field2', 'field3']


class NestedSerializersTestSerializer(serializers.Serializer):
    model = ModelTestSerializer()
    models = ModelTestSerializer(many=True)
    models_nullable = ModelTestSerializer(many=True, allow_null=True)
