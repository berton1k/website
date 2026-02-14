import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Curator

SECRET = "SUPER_SECRET_KEY_123"

def auth(request):
    return request.headers.get("X-BOT-KEY") == SECRET

@csrf_exempt
def api_update_curator(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if request.headers.get("X-API-KEY") != "SUPER_SECRET_KEY":
        return JsonResponse({"error": "Forbidden"}, status=403)

    data = json.loads(request.body)

    curator, _ = Curator.objects.get_or_create(
        discord_id=data["discord_id"],
        defaults={
            "nickname": data["nickname"]
        }
    )

    curator.faction = data.get("faction")
    curator.messages = data.get("messages", 0)
    curator.replies = data.get("replies", 0)
    curator.reactions = data.get("reactions", 0)
    curator.voice_minutes = data.get("voice_minutes", 0)

    curator.score = (
        curator.messages * 2 +
        curator.replies * 3 +
        curator.reactions * 1 +
        (curator.voice_minutes // 60) * 10
    )

    curator.save()

    return JsonResponse({"ok": True})

