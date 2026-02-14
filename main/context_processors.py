def access_flags(request):
    user = request.session.get("user")
    discord_id = str(user["id"]) if user else None

    ALLOWED_IDS = [
        "965947020026191922",
        "1072166657549676726",
    ]

    return {
        "is_admin_panel": discord_id in ALLOWED_IDS,
        "discord_user": user,
    }
