# DRF Typescript generator

This package allows you to generate typescript types / interfaces for Django REST framework
serializers, which can be then simply used in frontend applications.

## Setup

Install the package with your preferred dependency management tool:

```console
$ poetry add drf-typescript-generator
```

Add `drf_typescript_generator` to `INSTALLED_APPS` in your django settings&#46;py file:


```python
INSTALLED_APPS = [
    ...
    'drf_typescript_generator',
    ...
]
```

## Usage

To generate types run django management command `generate_types` with the names of django apps
you want the script to look for serializers in:

```console
$ python manage.py generate_types my_app
```

Example serializer found in *my_app*:

```python
class MySerializer(serializers.Serializer):
    some_string = serializers.CharField(max_length=100)
    some_number = serializers.IntegerField()
    some_boolean = serializers.BooleanField()
    choice = serializers.ChoiceField(
        choices=[1, 2, 3],
        allow_null=True
    )
    multichoice = serializers.MultipleChoiceField(
        choices=[2, 3, 5]
    )
```

Generated typescript type:

```typescript
export type MySerializer = {
  choice: 1 | 2 | 3 | null
  multichoice: (2 | 3 | 5)[]
  someBoolean: boolean
  someNumber: number
  someString: string
}
```

The script looks for classes that inherit from `APIView` in project urls&#46;py file as well as urls&#46;py
files in given apps. It then extracts serializers which are used in modules of found classes. This approach
cover `Views` as well as `ViewSets`.

### Arguments

The `generate_types` command supports following arguments:

| Argument | Value type | Description | Default value |
| --- | --- | --- | --- |
| `--format` | "type" \| "interface" | Whether to output typescript types or interfaces | "type"
| `--semicolons` | boolean | If the argument is present semicolons will be added in output | False
| `--spaces` | int | Output indentation will use given number of spaces (mutually exclusive with `--tabs`). Spaces are used if neither `--spaces` nor `--tabs` argument is present. | 2
| `--tabs` | int | Output indentation will use given number of tabs (mutually exclusive with `--spaces`) | None

## Features

The package currently supports following features that are correctly transformed to typescript syntax:

- [X] Basic serializers
- [X] Model serializers
- [X] Nested serializers
- [X] Method fields (typed with correct type if python type hints are used)
- [X] Required / optional fields
- [X] List fields 
- [X] Choice and multiple choice fields (results in composite typescript type)
- [X] allow_blank, allow_null (results in composite typescript type)

More features are planned to add later on:

- [ ] One to many and many to many fields correct typing
- [ ] Differentiate between read / write only fields while generating type / interface
- [ ] Integration with tools like [drf_yasg](https://github.com/axnsan12/drf-yasg) to allow downloading the
generated type from the documentation of the API
- [ ] Accept custom mappings
