"""View functions for partials."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.timezone import localtime

from main.models import DruncMessage
from main.views.utils import handle_errors


@login_required
@handle_errors
def messages(request: HttpRequest, topic: str) -> HttpResponse:
    """Search and render Kafka messages from the database."""
    search = request.GET.get("search", "")
    records = DruncMessage.objects.filter(
        topic__regex=settings.KAFKA_TOPIC_REGEX[topic], message__icontains=search
    ).order_by("-timestamp")

    # Time is stored as UTC. localtime(t) converts this to our configured timezone.
    messages = [
        {
            "timestamp": localtime(record.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "severity": record.severity,
            "message": record.message,
            "topic": record.topic,
        }
        for record in records
    ]

    return render(
        request=request,
        context={"messages": messages},
        template_name="main/partials/message_items.html",
    )
