# Copyright (c) 2023-present Taskflow Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

# Django imports
from django.db.models import Count

# Third party imports
from rest_framework import status
from rest_framework.response import Response

# Module imports
from taskflow.app.serializers import IssueTaskParameterValueSerializer, ProjectTaskParameterSerializer
from taskflow.app.views.base import BaseAPIView, BaseViewSet
from taskflow.db.models import Issue, IssueTaskParameterValue, ProjectMember, ProjectTaskParameter, WorkspaceMember
from taskflow.db.models.project import ROLE
from taskflow.app.serializers.project_parameter import upsert_issue_parameter_values


def is_project_or_workspace_admin(user, slug, project_id):
    if ProjectMember.objects.filter(
        member=user,
        workspace__slug=slug,
        project_id=project_id,
        role=ROLE.ADMIN.value,
        is_active=True,
    ).exists():
        return True

    return WorkspaceMember.objects.filter(
        member=user,
        workspace__slug=slug,
        role=ROLE.ADMIN.value,
        is_active=True,
    ).exists()


class ProjectTaskParameterViewSet(BaseViewSet):
    model = ProjectTaskParameter
    serializer_class = ProjectTaskParameterSerializer

    def get_queryset(self):
        queryset = (
            ProjectTaskParameter.objects.filter(
                workspace__slug=self.kwargs.get("slug"),
                project_id=self.kwargs.get("project_id"),
            )
            .annotate(value_count=Count("issue_values", distinct=True))
            .order_by("sort_order", "created_at")
        )
        if self.action == "list" and self.request.GET.get("all") != "true":
            queryset = queryset.filter(is_active=True)
        return queryset

    def _has_project_access(self, request, slug, project_id):
        return ProjectMember.objects.filter(
            member=request.user,
            workspace__slug=slug,
            project_id=project_id,
            is_active=True,
        ).exists()

    def list(self, request, slug, project_id):
        if not self._has_project_access(request, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, slug, project_id, pk=None):
        if not self._has_project_access(request, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(self.get_queryset().get(pk=pk))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, slug, project_id):
        if not is_project_or_workspace_admin(request.user, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={"project_id": project_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, slug, project_id, pk=None):
        if not is_project_or_workspace_admin(request.user, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        parameter = self.get_queryset().get(pk=pk)
        serializer = self.get_serializer(parameter, data=request.data, context={"project_id": project_id}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, slug, project_id, pk=None):
        if not is_project_or_workspace_admin(request.user, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        parameter = self.get_queryset().get(pk=pk)
        if IssueTaskParameterValue.objects.filter(parameter=parameter).exists():
            parameter.is_active = False
            parameter.save()
        else:
            parameter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueTaskParameterValueEndpoint(BaseAPIView):
    def _get_issue(self, slug, project_id, issue_id):
        return Issue.objects.get(workspace__slug=slug, project_id=project_id, pk=issue_id)

    def _can_read_issue(self, request, slug, project_id):
        return ProjectMember.objects.filter(
            member=request.user,
            workspace__slug=slug,
            project_id=project_id,
            is_active=True,
        ).exists()

    def _can_edit_issue(self, request, slug, project_id, issue):
        if issue.created_by_id == request.user.id:
            return True

        return ProjectMember.objects.filter(
            member=request.user,
            workspace__slug=slug,
            project_id=project_id,
            role__in=[ROLE.ADMIN.value, ROLE.MEMBER.value],
            is_active=True,
        ).exists()

    def get(self, request, slug, project_id, issue_id):
        if not self._can_read_issue(request, slug, project_id):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        issue = self._get_issue(slug, project_id, issue_id)
        values = IssueTaskParameterValue.objects.filter(issue=issue).select_related("parameter")
        serializer = IssueTaskParameterValueSerializer(values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, slug, project_id, issue_id):
        issue = self._get_issue(slug, project_id, issue_id)
        if not self._can_edit_issue(request, slug, project_id, issue):
            return Response({"error": "You don't have the required permissions."}, status=status.HTTP_403_FORBIDDEN)

        parameter_values = request.data.get("parameter_values", request.data)
        values = upsert_issue_parameter_values(issue=issue, parameter_values=parameter_values)
        serializer = IssueTaskParameterValueSerializer(values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
