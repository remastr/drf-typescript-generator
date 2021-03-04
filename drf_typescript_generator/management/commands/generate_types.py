from django.apps import AppConfig
from django.core.management.base import AppCommand

from drf_typescript_generator.utils import (
    get_app_serializers,
    get_serializer_fields,
)


class Command(AppCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--format', type=str, choices=['types', 'interfaces'], default='types',
            help='Specifies whether the result will be types or interfaces'
        )
        return super().add_arguments(parser)

    def handle_app_config(self, app_config: AppConfig, **options):
        serializers = get_app_serializers(app_config.name)
        for serializer_name, serializer in serializers:
            fields = get_serializer_fields(serializer)
            self.export_serializer(serializer_name, fields, options['format'])

    def export_serializer(self, serializer_name, fields, output_format):
        def format_field(field):
            return f'\t{field[0]}: {field[1]};'

        attributes = '\n'.join([format_field(field) for field in fields.items()])

        if output_format == "types":
            template = 'export type {} = {{\n{}\n}}'
        else:
            template = 'export interface {} {{\n{}\n}}'

        self.stdout.write(template.format(serializer_name, attributes))



