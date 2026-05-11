# Copyright (c) 2023-present Taskflow Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
import re

# Django imports
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.dateparse import parse_date

# Third party imports
from rest_framework import serializers

# Module imports
from .base import BaseSerializer
from taskflow.db.models import IssueTaskParameterValue, ProjectTaskParameter, ProjectTaskParameterType


PARAMETER_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def get_parameter_option_ids(options):
    choices = options.get("choices") if isinstance(options, dict) else None
    if choices is None:
        choices = options.get("options") if isinstance(options, dict) else None
    if not isinstance(choices, list):
        return set()
    return {str(choice.get("id")) for choice in choices if isinstance(choice, dict) and choice.get("id")}


def validate_parameter_options(parameter_type, options):
    if options in (None, ""):
        options = {}
    if not isinstance(options, dict):
        raise serializers.ValidationError("Options must be an object.")

    if parameter_type in [
        ProjectTaskParameterType.SINGLE_SELECT.value,
        ProjectTaskParameterType.MULTI_SELECT.value,
    ]:
        choices = options.get("choices", options.get("options"))
        if not isinstance(choices, list) or len(choices) == 0:
            raise serializers.ValidationError("Select parameters require at least one option.")

        option_ids = set()
        for choice in choices:
            if not isinstance(choice, dict):
                raise serializers.ValidationError("Each option must be an object.")
            option_id = choice.get("id")
            label = choice.get("label")
            if not option_id or not isinstance(option_id, str):
                raise serializers.ValidationError("Each option requires a stable string id.")
            if not label or not isinstance(label, str):
                raise serializers.ValidationError("Each option requires a label.")
            if option_id in option_ids:
                raise serializers.ValidationError("Option ids must be unique.")
            option_ids.add(option_id)

    return options


def validate_parameter_value_by_type(parameter_type, options, value, is_required=False):
    if value in (None, ""):
        if is_required:
            raise serializers.ValidationError("This parameter is required.")
        return None

    if parameter_type == ProjectTaskParameterType.TEXT.value:
        if not isinstance(value, str):
            raise serializers.ValidationError("Text parameter values must be strings.")
        return value

    if parameter_type == ProjectTaskParameterType.NUMBER.value:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise serializers.ValidationError("Number parameter values must be numbers.")
        return value

    if parameter_type == ProjectTaskParameterType.DATE.value:
        if not isinstance(value, str) or parse_date(value) is None:
            raise serializers.ValidationError("Date parameter values must use YYYY-MM-DD format.")
        return value

    if parameter_type == ProjectTaskParameterType.BOOLEAN.value:
        if not isinstance(value, bool):
            raise serializers.ValidationError("Boolean parameter values must be true or false.")
        return value

    if parameter_type == ProjectTaskParameterType.URL.value:
        if not isinstance(value, str):
            raise serializers.ValidationError("URL parameter values must be strings.")
        validator = URLValidator()
        try:
            validator(value)
        except DjangoValidationError:
            raise serializers.ValidationError("URL parameter value is invalid.")
        return value

    option_ids = get_parameter_option_ids(options)

    if parameter_type == ProjectTaskParameterType.SINGLE_SELECT.value:
        if not isinstance(value, str) or value not in option_ids:
            raise serializers.ValidationError("Single select parameter value must be one valid option id.")
        return value

    if parameter_type == ProjectTaskParameterType.MULTI_SELECT.value:
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise serializers.ValidationError("Multi select parameter values must be a list of option ids.")
        invalid_values = [item for item in value if item not in option_ids]
        if invalid_values:
            raise serializers.ValidationError("Multi select parameter value contains invalid option ids.")
        return value

    raise serializers.ValidationError("Unsupported parameter type.")


def validate_parameter_value(parameter, value):
    return validate_parameter_value_by_type(
        parameter_type=parameter.type,
        options=parameter.options,
        value=value,
        is_required=parameter.is_required,
    )


def upsert_issue_parameter_values(issue, parameter_values):
    if parameter_values is None:
        return []

    parameter_values = validate_issue_parameter_values(issue.project_id, parameter_values)

    result = []
    project_parameters = {
        str(parameter.id): parameter for parameter in ProjectTaskParameter.objects.filter(project=issue.project)
    }
    for item in parameter_values:
        parameter_id = str(item.get("parameter_id") or item.get("parameter"))
        parameter = project_parameters[parameter_id]

        parameter_value, _ = IssueTaskParameterValue.objects.update_or_create(
            issue=issue,
            parameter=parameter,
            defaults={
                "value": item.get("value"),
                "project": issue.project,
                "workspace": issue.workspace,
            },
        )
        result.append(parameter_value)

    return result


def validate_issue_parameter_values(project_id, parameter_values):
    if parameter_values is None:
        return []

    if not isinstance(parameter_values, list):
        raise serializers.ValidationError({"parameter_values": "Parameter values must be a list."})

    project_parameters = {
        str(parameter.id): parameter
        for parameter in ProjectTaskParameter.objects.filter(project_id=project_id, is_active=True)
    }

    validated_values = []
    for item in parameter_values:
        if not isinstance(item, dict):
            raise serializers.ValidationError({"parameter_values": "Each parameter value must be an object."})

        parameter_id = str(item.get("parameter_id") or item.get("parameter"))
        if parameter_id not in project_parameters:
            raise serializers.ValidationError({"parameter_values": "Parameter does not belong to this project."})

        parameter = project_parameters[parameter_id]
        validated_values.append(
            {
                "parameter_id": parameter_id,
                "value": validate_parameter_value(parameter, item.get("value")),
            }
        )

    return validated_values


class ProjectTaskParameterSerializer(BaseSerializer):
    value_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTaskParameter
        fields = "__all__"
        read_only_fields = ["workspace", "project", "deleted_at", "created_by", "updated_by", "value_count"]

    def validate_key(self, value):
        value = value.strip().lower()
        if not PARAMETER_KEY_PATTERN.match(value):
            raise serializers.ValidationError(
                "Key must start with a letter or number and contain only lowercase letters, numbers, "
                "underscores, or hyphens."
            )
        return value

    def get_value_count(self, obj):
        return getattr(obj, "value_count", None)

    def validate(self, attrs):
        parameter_type = attrs.get("type", self.instance.type if self.instance else ProjectTaskParameterType.TEXT.value)
        options = validate_parameter_options(
            parameter_type,
            attrs.get("options", self.instance.options if self.instance else {}),
        )

        if self.instance and "type" in attrs and attrs["type"] != self.instance.type:
            has_values = IssueTaskParameterValue.objects.filter(parameter=self.instance).exists()
            if has_values:
                raise serializers.ValidationError({"type": "Type cannot be changed after values exist."})

        if "default_value" in attrs:
            validate_parameter_value_by_type(
                parameter_type=parameter_type,
                options=options,
                value=attrs.get("default_value"),
                is_required=False,
            )

        attrs["options"] = options
        return attrs

    def create(self, validated_data):
        return ProjectTaskParameter.objects.create(**validated_data, project_id=self.context["project_id"])


class IssueTaskParameterValueSerializer(BaseSerializer):
    parameter_detail = ProjectTaskParameterSerializer(source="parameter", read_only=True)
    parameter_id = serializers.UUIDField(source="parameter.id", read_only=True)

    class Meta:
        model = IssueTaskParameterValue
        fields = [
            "id",
            "issue",
            "parameter",
            "parameter_id",
            "parameter_detail",
            "value",
            "workspace",
            "project",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = fields
