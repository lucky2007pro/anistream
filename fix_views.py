import re

with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add missing imports
if 'ZoneInfo' not in content:
    content = content.replace('from django.http import JsonResponse', "from django.http import JsonResponse\nfrom zoneinfo import ZoneInfo\nfrom django.utils.timezone import localtime\nfrom django.contrib.auth.models import User")

# 2. Fix select_related
content = content.replace("'user__avatar', 'user__vip_data'", "'user__profile'")
content = content.replace("'user', 'user__avatar', 'user__vip_data', 'reply_to'", "'user', 'user__profile', 'reply_to'")
content = content.replace("'user', 'user__avatar', 'reply_to', 'reply_to__user'", "'user', 'user__profile', 'reply_to', 'reply_to__user'")

# 3. Fix avatar fetching logic
content = re.sub(r"avatar_url = msg\.user\.avatar\.image\.url if getattr\(msg\.user, 'avatar', None\) and msg\.user\.avatar\.image else None", 
                 "avatar_url = msg.user.profile.avatar_url if hasattr(msg.user, 'profile') and msg.user.profile.avatar_url else None", content)

content = re.sub(r"avatar_url = None\s+if getattr\(c\.user, 'avatar', None\) and c\.user\.avatar\.image:\s+avatar_url = c\.user\.avatar\.image\.url",
                 "avatar_url = c.user.profile.avatar_url if hasattr(c.user, 'profile') and c.user.profile.avatar_url else None", content)

content = re.sub(r"avatar_url = None\s+if getattr\(request\.user, 'avatar', None\) and request\.user\.avatar\.image:\s+avatar_url = request\.user\.avatar\.image\.url",
                 "avatar_url = request.user.profile.avatar_url if hasattr(request.user, 'profile') and request.user.profile.avatar_url else None", content)

# 4. Fix VIP fetching
content = re.sub(r"hasattr\(msg\.user, 'vip_data'\) and msg\.user\.vip_data\.vip_active\(\)", "hasattr(msg.user, 'profile') and msg.user.profile.is_premium", content)

# 5. Fix is_banned and is_admin_user logic
content = content.replace("request.user.is_banned", "not request.user.is_active")
content = content.replace("msg.user.is_admin_user", "msg.user.is_staff")
content = content.replace("request.user.is_admin_user", "request.user.is_staff")

# Fix ban_user view specifically
ban_user_replacement = """@login_required
def ban_user(request, user_id):
    if not request.user.is_staff:
        return redirect('chat')
    user_to_ban = get_object_or_404(User, id=user_id)
    if not user_to_ban.is_staff:
        user_to_ban.is_active = False
        user_to_ban.save()
    return redirect('chat')"""

content = re.sub(r"@login_required\s*def ban_user\(request, user_id\):.*?return redirect\('chat'\)", ban_user_replacement, content, flags=re.DOTALL)

with open('d:/anime/anistream/anime/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("views.py fixed successfully.")
