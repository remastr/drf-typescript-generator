from django.apps import AppConfig
from django.core.management.base import AppCommand

from drf_typescript_generator.utils import (
    export_serializer,
    get_app_routers,
    get_module_serializers,
    get_project_routers,
    get_serializer_fields,
)


class Command(AppCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_routers = get_project_routers()
        self.already_parsed = set()

    def add_arguments(self, parser):
        parser.add_argument(
            '--format', type=str, choices=['type', 'interface'], default='types',
            help='Specifies whether the result will be types or interfaces'
        )
        parser.add_argument(
            '--semicolons', action='store_true', default=False,
            help='Semicolons will be added if this argument is present'
        )
        return super().add_arguments(parser)

    def handle_app_config(self, app_config: AppConfig, **options):
        # find routers in app urls and project urls
        routers = [router[1] for router in self.project_routers + get_app_routers(app_config.name)]
        views_modules = set()
        serializers = set()

        # find modules containing viewsets in the app (views.py, api.py, etc.)
        for router in routers:
            for _, viewset_class, _ in router.registry:
                module = viewset_class.__module__
                if module.split('.')[0] == app_config.name:
                    views_modules.add(module)

        # extract all serializers found in views modules
        for module in views_modules:
            serializers = serializers.union(get_module_serializers(module))

        for serializer_name, serializer in sorted(serializers):
            if serializer_name not in self.already_parsed:
                fields = get_serializer_fields(serializer)
                ts_serializer = export_serializer(serializer_name, fields, options['format'], options['semicolons'])
                self.already_parsed.add(serializer_name)
                self.stdout.write(ts_serializer)
