from rest_framework import serializers


DEFAULT_TYPE = 'any'

MAPPING = {
    # boolean fields
    serializers.BooleanField: 'boolean',
    serializers.NullBooleanField: 'boolean',

    # string fields
    serializers.CharField: 'string',
    serializers.EmailField: 'string',
    serializers.RegexField: 'string',
    serializers.SlugField: 'string',
    serializers.URLField: 'string',
    serializers.UUIDField: 'string',
    serializers.FilePathField: 'string',
    serializers.IPAddressField: 'string',

    # numeric fields
    serializers.IntegerField: 'number',
    serializers.FloatField: 'number',
    serializers.DecimalField: 'number',

    # date and time fields TODO: correct format depending on settings?
    serializers.DateTimeField: 'string',
    serializers.DateField: 'string',
    serializers.TimeField: 'string',
    serializers.DurationField: 'string',

    # choice selection fields TODO: export also choices?
    # TODO: file upload fields?

    # method return values
    str: 'string',
    int: 'number',
    float: 'number',
    bool: 'boolean'
    # TODO: add more
}

# field types which require special treatment
SPECIAL_FIELD_TYPES = [
    serializers.SerializerMethodField,
    serializers.ChoiceField,
    serializers.MultipleChoiceField
]


CHOICES_TRANSFORM_FUNCTIONS_BY_TYPE = {
    str: lambda x: f'"{x}"',
    int: lambda x: x,
    float: lambda x: x,
    bool: lambda x: str(x).lower()
}


