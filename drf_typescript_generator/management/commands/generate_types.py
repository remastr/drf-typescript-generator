from django.apps import AppConfig
from django.core.management.base import AppCommand

from drf_typescript_generator.utils import (
    get_app_serializers,
    get_serializer_fields,
)


class Command(AppCommand):
    def export_serializer_type(self, serializer_name, fields):
        def format_field(field):
            return f'\t{field[0]}: {field[1]};'

        foo = '\n'.join([format_field(field) for field in fields.items()])
        self.stdout.write(
            f'export type {serializer_name} = {{\n{foo}\n}}'
        )

    def handle_app_config(self, app_config: AppConfig, **options):
        serializers = get_app_serializers(app_config.name)
        for serializer_name, serializer in serializers:
            fields = get_serializer_fields(serializer)
            self.export_serializer_type(serializer_name, fields)


