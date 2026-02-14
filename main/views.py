from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Suggestion
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout
import json
from .models import Curator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import os
import requests
from django.urls import reverse
import sqlite3
from django.http import HttpResponseForbidden
from main.models import Server, Backup

# ---------- Логин через дискорд ----------
def discord_login(request):
    client_id = os.getenv("DISCORD_OAUTH_CLIENT_ID")
    redirect_uri = os.getenv("DISCORD_OAUTH_REDIRECT")

    url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        "&scope=identify%20guilds%20guilds.members.read"
        f"&redirect_uri={redirect_uri}"
    )

    return redirect(url)

def discord_callback(request):
    code = request.GET.get("code")
    if not code:
        request.session["login_error"] = "Ошибка авторизации Discord"
        return redirect("login")

    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": os.getenv("DISCORD_OAUTH_CLIENT_ID"),
            "client_secret": os.getenv("DISCORD_OAUTH_CLIENT_SECRET"),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("DISCORD_OAUTH_REDIRECT"),
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")

    if not access_token:
        request.session["login_error"] = "Не удалось получить токен Discord"
        return redirect("login")

    headers = {"Authorization": f"Bearer {access_token}"}

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers=headers
    ).json()

    guild_id = os.getenv("DISCORD_GUILD_ID")
    role_id = os.getenv("DISCORD_ADMIN_ROLE")

    member = requests.get(
        f"https://discord.com/api/users/@me/guilds/{guild_id}/member",
        headers=headers,
    )

    if member.status_code != 200:
        request.session["login_error"] = "Вы не на сервере Discord"
        return redirect("login")

    roles = member.json().get("roles", [])

    if role_id not in roles:
        request.session["login_error"] = "Вы не администратор"
        return redirect("login")

    # ✅ if good - login
    request.session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "avatar": user["avatar"],
    }
    request.session["login_success"] = "Вы успешно авторизовались"
    request.session.modified = True

    return redirect("/")

def some_protected_view(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("login")

    if not user.groups.filter(name="Admin").exists():
        messages.error(request, "Вы не администратор")
        return redirect("login")

    # if good
    return render(request, "main/index.html")

def clear_login_error(request):
    request.session.pop("login_error", None)
    return JsonResponse({"ok": True})

def clear_login_success(request):
    request.session.pop("login_success", None)
    return JsonResponse({"ok": True})

# ---------- Main ----------
def index(request):
    qs = Curator.objects.order_by("-score")

    filter_type = request.GET.get("type")

    if filter_type == "gov":
        qs = qs.filter(curator_types__icontains="government")
    elif filter_type == "crime":
        qs = qs.filter(curator_types__icontains="criminal")
    else:
        filter_type = None

    if request.user_agent.is_mobile:
        per_page = 2
    else:
        per_page = 6

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "main/index.html", {
        "page_obj": page_obj,
        "filter_type": filter_type
    })



def login(request):
    return render(request, 'main/login.html')


# ---------- Login ----------
USERS = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3",
    "user4": 'password4',
    "user5": 'password5'
}

def login_view(request):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    username = request.POST.get("login")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return JsonResponse({"ok": True})
    else:
        return JsonResponse({"ok": False})




def logout_view(request):
    logout(request)
    return redirect("login")

# ---------- Settings ----------
def settings_view(request):
    return render(request, 'main/settings.html')

# ---------- Suggestions ----------
def suggestions(request):
    if not request.session.get("user"):
        return redirect("login")

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Suggestion.objects.create(
                text=text,
                author=request.session["user"]["username"]
            )
        return redirect("suggestions")

    qs = Suggestion.objects.filter(viewed=False).order_by("-created_at")
    paginator = Paginator(qs, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "main/suggestions.html", {
        "page_obj": page_obj
    })

# ---------- Viewed ----------
def viewed(request):
    qs = Suggestion.objects.filter(viewed=True).order_by("-created_at")

    if request.user_agent.is_mobile:
        per_page = 4
    else:
        per_page = 6

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "main/viewed.html", {
        "page_obj": page_obj
    })


# ---------- Move ----------
def move_post(request, pk):
    post = Suggestion.objects.get(pk=pk)
    post.viewed = True
    post.save()
    return redirect("suggestions")

@csrf_exempt
def sync_curator(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "Forbidden"}, status=403)
    data = json.loads(request.body)

    curator, _ = Curator.objects.get_or_create(
        discord_id=data["discord_id"]
    )

    curator.discord_username = (
        data.get("discord_username")
        or data.get("nickname")
        or data.get("username")
        or data.get("global_name")
    )


    curator.server_nickname = (
        data.get("nick")
        or data.get("server_nickname")
        or data.get("member", {}).get("nick")
        or data.get("global_name")
    )

    curator.factions = data.get("factions", curator.factions)
    curator.curator_types = data.get("curator_types", curator.curator_types)
    curator.online = data.get("online", curator.online)

    curator.messages += data.get("messages", 0)
    curator.replies += data.get("replies", 0)
    curator.reactions += data.get("reactions", 0)
    curator.voice_minutes += data.get("voice_minutes", 0)

    curator.score = (
        curator.messages * 2 +
        curator.replies * 3 +
        curator.reactions +
        (curator.voice_minutes // 60) * 10
    )

    curator.save()
    return JsonResponse({"ok": True})

@csrf_exempt
def remove_curator(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "Forbidden"}, status=403)

    data = json.loads(request.body)

    Curator.objects.filter(discord_id=data["discord_id"]).delete()
    return JsonResponse({"ok": True})

@csrf_exempt
def list_curators(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "Forbidden"}, status=403)

    data = list(
        Curator.objects.values("discord_id")
    )

    return JsonResponse(data, safe=False)

@csrf_exempt
def delete_curator(request, discord_id):
    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "Forbidden"}, status=403)

    Curator.objects.filter(discord_id=discord_id).delete()
    return JsonResponse({"ok": True})


ALLOWED_IDS = [
    '965947020026191922',
    '1072166657549676726'
]

BOT_API_URL = "http://url/stats"
API_TOKEN = settings.SITE_API_TOKEN

def stats_page(request):
    user = request.session.get("user")
    discord_id = str(user["id"]) if user else None

    if discord_id not in ALLOWED_IDS:
        return HttpResponseForbidden("⛔ Доступ запрещён")

    return render(request, "main/stats.html")

def api_stats(request):
    try:
        res = requests.get(
            f"{settings.BOT_API_BASE}/stats",
            headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
            timeout=5
        )

        res.raise_for_status()
        return JsonResponse(res.json())

    except Exception:
        return JsonResponse({
            "error": "bot_offline"
        }, status=503)
    
def api_servers(request):
    if not request.session.get("user"):
        return JsonResponse({"servers": []})

    try:
        res = requests.get(
            f"{settings.BOT_API_BASE}/api/servers",
            headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
            timeout=10
        )
        res.raise_for_status()

        Server.objects.all().update(active=False)

        for s in res.json().get("servers", []):
            Server.objects.update_or_create(
                discord_id=s["id"],
                defaults={
                    "name": s["name"],
                    "icon": s.get("icon"),
                    "active": True
                }
            )

    except Exception as e:
        print("SERVER SYNC FAILED:", e)

    servers = Server.objects.filter(active=True)

    return JsonResponse({
        "servers": [
            {
                "id": s.id,
                "discord_id": str(s.discord_id),
                "name": s.name,
                "icon": s.icon
            }
            for s in servers
        ]
    })

@csrf_exempt
def api_backup_create(request):
    if not request.session.get("user"):
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        data = json.loads(request.body)
        server_discord_id = str(data["server_id"])
    except Exception:
        return JsonResponse({"error": "bad_request"}, status=400)

    try:
        server = Server.objects.get(discord_id=server_discord_id)
    except Server.DoesNotExist:
        return JsonResponse({"error": "server_not_found"}, status=404)

    try:
        bot_res = requests.post(
            f"{settings.BOT_API_BASE}/api/backup/create",
            json={"server_id": str(server.discord_id)},
            headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
            timeout=30
        )
    except Exception as e:
        return JsonResponse(
            {"error": "bot_unreachable", "detail": str(e)},
            status=500
        )

    if bot_res.status_code != 200:
        return JsonResponse(
            {
                "error": "bot_error",
                "status": bot_res.status_code,
                "raw": bot_res.text
            },
            status=500
        )

    try:
        payload = bot_res.json()
        backup_id = payload["backup_id"]
    except Exception:
        return JsonResponse(
            {"error": "invalid_bot_response", "raw": bot_res.text},
            status=500
        )

    Backup.objects.create(
        server=server,
        backup_id=backup_id
    )

    return JsonResponse({
        "ok": True,
        "backup_id": backup_id
    })

@csrf_exempt
def api_server_sync(request):
    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "forbidden"}, status=403)

    data = json.loads(request.body)

    server, _ = Server.objects.update_or_create(
        discord_id=data["discord_id"],
        defaults={
            "name": data["name"],
            "icon": data.get("icon"),
            "owner_id": data.get("owner_id"),
        }
    )

    return JsonResponse({"ok": True, "id": server.id})
    
@csrf_exempt
def api_backup_restore(request):
    if not request.session.get("user"):
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        data = json.loads(request.body)
        backup_id = data["backup_id"]
        server_id = str(data["server_id"])
    except Exception as e:
        return JsonResponse({"error": "bad_request", "detail": str(e)}, status=400)

    try:
        server = Server.objects.get(discord_id=server_id)
    except Server.DoesNotExist:
        return JsonResponse({"error": "server_not_found"}, status=404)

    if server.backup_in_progress:
        return JsonResponse({"error": "backup_in_progress"}, status=409)

    server.backup_in_progress = True
    server.save(update_fields=["backup_in_progress"])

    try:
        bot_res = requests.post(
            f"{settings.BOT_API_BASE}/api/backup/restore",
            json={
                "backup_id": backup_id,
                "server_id": str(server.discord_id)
            },
            headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
            timeout=300
        )
    except Exception as e:
        server.backup_in_progress = False
        server.save(update_fields=["backup_in_progress"])
        return JsonResponse({"error": "bot_unreachable", "detail": str(e)}, status=500)

    if bot_res.status_code != 200:
        server.backup_in_progress = False
        server.save(update_fields=["backup_in_progress"])
        return JsonResponse({
            "error": "bot_error",
            "status": bot_res.status_code,
            "raw": bot_res.text
        }, status=bot_res.status_code)
    backup = Backup.objects.get(backup_id=backup_id)

    if str(backup.server.discord_id) == server_id:
        server.backup_in_progress = False
        server.save(update_fields=["backup_in_progress"])
        return JsonResponse({
            "error": "same_server_restore_forbidden"
        }, status=400)

    return JsonResponse({"ok": True})

def api_mass_status(request):
    res = requests.get(
        f"{settings.BOT_API_URL.replace('/stats', '')}/status/actions",
        headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
        timeout=3
    )

    return JsonResponse(res.json())

def api_backups(request):
    if not request.session.get("user"):
        return JsonResponse({"backups": []})

    discord_id = request.GET.get("server_id")
    if not discord_id:
        return JsonResponse({"backups": []})

    backups = Backup.objects.filter(
        server__discord_id=discord_id
    ).order_by("-created_at")

    return JsonResponse({
        "backups": [
            {
                "backup_id": b.backup_id,
                "created_at": b.created_at.isoformat()
            }
            for b in backups
        ]
    })

@csrf_exempt
def api_server_status(request):
    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "forbidden"}, status=403)

    data = json.loads(request.body)
    server_id = int(data["server_id"])

    try:
        server = Server.objects.get(discord_id=server_id)
    except Server.DoesNotExist:
        return JsonResponse({"error": "server_not_found"}, status=404)

    if server.backup_in_progress:
        return JsonResponse({"error": "backup_in_progress"}, status=409)

    return JsonResponse({"ok": True})

@csrf_exempt
def api_backup_finish(request):
    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "forbidden"}, status=403)

    data = json.loads(request.body)
    server_id = str(data["server_id"])

    try:
        server = Server.objects.get(discord_id=server_id)
    except Server.DoesNotExist:
        return JsonResponse({"error": "server_not_found"}, status=404)

    server.backup_in_progress = False
    server.save(update_fields=["backup_in_progress"])

    request.session["backup_finished"] = server_id
    request.session.modified = True

    return JsonResponse({"ok": True})

def api_backup_status(request):
    finished = request.session.pop("backup_finished", None)
    request.session.modified = True
    return JsonResponse({"finished": bool(finished)})

@csrf_exempt
def api_servers_sync(request):
    if request.headers.get("Authorization") != f"Bearer {settings.SITE_API_TOKEN}":
        return JsonResponse({"error": "forbidden"}, status=403)

    try:
        res = requests.get(
            f"{settings.BOT_API_BASE}/api/servers",
            headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
            timeout=10
        )
        res.raise_for_status()
    except Exception:
        return JsonResponse({"error": "bot_unreachable"}, status=502)

    Server.objects.all().update(active=False)

    for s in res.json().get("servers", []):
        Server.objects.update_or_create(
            discord_id=s["id"],
            defaults={
                "name": s["name"],
                "icon": s.get("icon"),
                "active": True
            }
        )

    return JsonResponse({"ok": True})

def clear_page(request):
    user = request.session.get("user")
    discord_id = str(user["id"]) if user else None

    if discord_id not in ALLOWED_IDS:
        return HttpResponseForbidden("⛔ Доступ запрещён")

    return render(request, "main/clear.html")

CLEAR_BLOCKED_SERVERS = {
    "1454623903006593026",
    "1451990978452787382",
    "1451891816604631081",
    "1452687907801530461",
}

@csrf_exempt
def api_clear_server(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.session.get("user"):
        return JsonResponse({"error": "forbidden"}, status=403)

    data = json.loads(request.body)
    guild_id = str(data.get("guild_id"))
    
    if guild_id in CLEAR_BLOCKED_SERVERS:
        return JsonResponse({
            "blocked": True,
            "reason": "server_blocked"
        })

    res = requests.post(
        f"{settings.BOT_API_BASE}/api/clear",
        json={"guild_id": guild_id},
        headers={"Authorization": f"Bearer {settings.SITE_API_TOKEN}"},
        timeout=10
    )

    try:
        data = res.json()
    except Exception:
        return JsonResponse({
            "error": "invalid_bot_response",
            "status": res.status_code,
            "raw": res.text
        }, status=500)

    return JsonResponse(data)
