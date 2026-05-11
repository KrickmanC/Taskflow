# Copyright (c) 2023-present Taskflow Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Python imports
from enum import Enum

# Django imports
from django.db import models
from django.db.models import Q

# Module imports
from .project import ProjectBaseModel


class ProjectTaskParameterType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    URL = "url"

    @classmethod
    def choices(cls):
        return [(item.value, item.value) for item in cls]


class ProjectTaskParameter(ProjectBaseModel):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    type = models.CharField(
        max_length=32,
        choices=ProjectTaskParameterType.choices(),
        default=ProjectTaskParameterType.TEXT.value,
    )
    options = models.JSONField(default=dict, blank=True)
    default_value = models.JSONField(null=True, blank=True)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.FloatField(default=65535)

    class Meta:
        verbose_name = "Project Task Parameter"
        verbose_name_plural = "Project Task Parameters"
        db_table = "project_task_parameters"
        ordering = ("sort_order", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=["project", "key"],
                condition=Q(deleted_at__isnull=True),
                name="project_task_parameter_unique_project_key_when_deleted_at_null",
            )
        ]

    def save(self, *args, **kwargs):
        self.key = self.key.strip().lower()
        super(ProjectTaskParameter, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} <{self.project.name}>"


class IssueTaskParameterValue(ProjectBaseModel):
    issue = models.ForeignKey(
        "db.Issue",
        on_delete=models.CASCADE,
        related_name="task_parameter_values",
    )
    parameter = models.ForeignKey(
        ProjectTaskParameter,
        on_delete=models.CASCADE,
        related_name="issue_values",
    )
    value = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Issue Task Parameter Value"
        verbose_name_plural = "Issue Task Parameter Values"
        db_table = "issue_task_parameter_values"
        ordering = ("parameter__sort_order", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=["issue", "parameter"],
                condition=Q(deleted_at__isnull=True),
                name="issue_task_parameter_value_unique_issue_parameter_when_deleted_at_null",
            )
        ]

    def save(self, *args, **kwargs):
        if self.issue_id and not self.project_id:
            self.project = self.issue.project
        if self.parameter_id and not self.project_id:
            self.project = self.parameter.project
        super(IssueTaskParameterValue, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.parameter.key} <{self.issue_id}>"
