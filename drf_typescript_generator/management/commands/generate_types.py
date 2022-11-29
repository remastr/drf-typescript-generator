from django.apps import AppConfig
from django.core.management.base import AppCommand

from drf_typescript_generator.utils import (
    export_serializer,
    get_module_serializers,
    get_nested_serializers,
    get_serializer_fields,
    get_project_api_views,
    get_app_api_views
)


class Command(AppCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.already_parsed = set()
        self.project_api_views = get_project_api_views()

    def add_arguments(self, parser):
        parser.add_argument(
            '--format', type=str, choices=['type', 'interface'], default='type',
            help='Specifies whether the result will be types or interfaces'
        )
        parser.add_argument(
            '--semicolons', action='store_true', default=False,
            help='Semicolons will be added if this argument is present'
        )
        parser.add_argument(
            '--preserve-case', action='store_true', default=False,
            help='Preserve field name case from serializers'
        )
        whitespace_group = parser.add_mutually_exclusive_group()
        whitespace_group.add_argument('--spaces', type=int, default=2)
        whitespace_group.add_argument('--tabs', type=int)

        return super().add_arguments(parser)

    def handle_app_config(self, app_config: AppConfig, **options):
        views_modules = set()
        serializers = set()

        for _name, api_view_class in self.project_api_views + get_app_api_views(app_config.name):
            module = api_view_class.__module__
            if module.startswith(app_config.name):
                views_modules.add(module)

        # extract all serializers found in views modules
        for module in views_modules:
            serializers = serializers.union(get_module_serializers(module))

        for serializer_name, serializer in sorted(serializers):
            self.process_serializer(serializer_name, serializer, options)

    def process_serializer(self, serializer_name, serializer, options):
        if serializer_name not in self.already_parsed:
            # recursively process nested serializers first to ensure that
            # TS equivalent is generated even if they are not used in views module
            nested_serializers = get_nested_serializers(serializer)
            for nested_serializer_name, nested_serializer in nested_serializers.items():
                self.process_serializer(nested_serializer_name, nested_serializer, options)

            fields = get_serializer_fields(serializer, options)
            ts_serializer = export_serializer(serializer_name, fields, options)
            self.already_parsed.add(serializer_name)
            self.stdout.write(ts_serializer)
