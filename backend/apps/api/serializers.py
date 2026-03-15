from __future__ import annotations

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class UploadUrlSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    mime_type = serializers.CharField(default="application/pdf")


class DocumentCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=False, allow_blank=True)
    source_channel = serializers.ChoiceField(choices=["web", "mobile", "email", "api"], default="web")
    file_name = serializers.CharField(required=False)
    mime_type = serializers.CharField(default="application/pdf")
    title = serializers.CharField(required=False, allow_blank=True)
    document_type_hint = serializers.CharField(required=False, allow_blank=True)
    vip_customer = serializers.BooleanField(default=False)
    force_review = serializers.BooleanField(default=False)
    file = serializers.FileField(required=False)
    minio_object_name = serializers.CharField(required=False, allow_blank=True)
    uploaded_via_presigned = serializers.BooleanField(default=False)
    reviewer_email = serializers.EmailField(required=False)


class ReviewActionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject", "request_changes"])
    reviewer_id = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)


class ReviewSubmitSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject", "request_changes"])
    reviewer_feedback = serializers.CharField(required=False, allow_blank=True)
    corrected_fields = serializers.DictField(required=False)


class TriggerReviewSerializer(serializers.Serializer):
    document_id = serializers.CharField()
    assigned_team = serializers.ChoiceField(
        choices=["operations", "fraud", "compliance", "customer_support"],
        default="operations",
    )
    reviewer_email = serializers.EmailField(required=False)
    instructions = serializers.CharField(required=False, allow_blank=True)


class SearchSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=10)


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
