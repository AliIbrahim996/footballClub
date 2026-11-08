"""Public "contact us" form: stored in the database and optionally e-mailed to the site owner."""
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import serializers, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import ContactMessage


class ContactSerializer(serializers.ModelSerializer):
    # Honeypot: real visitors never see or fill this field; bots usually do.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "club", "message", "locale", "website"]
        extra_kwargs = {"message": {"max_length": 4000}, "locale": {"max_length": 8}}


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([ScopedRateThrottle])
def contact(request):
    s = ContactSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    data = dict(s.validated_data)
    if data.pop("website", ""):
        return Response({"ok": True}, status=status.HTTP_201_CREATED)  # pretend success; store nothing
    msg = ContactMessage.objects.create(**data)
    if settings.CONTACT_EMAIL:
        send_mail(
            f"[Pitchside] Contact from {msg.name}",
            f"From: {msg.name} <{msg.email}>\nClub: {msg.club or '-'}\nLanguage: {msg.locale or '-'}\n\n{msg.message}",
            None, [settings.CONTACT_EMAIL], fail_silently=True,
        )
    return Response({"ok": True}, status=status.HTTP_201_CREATED)


contact.cls.throttle_scope = "contact"
