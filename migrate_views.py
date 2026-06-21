import re

with open('d:/anime/anime_zakaz/my_app/views.py', 'r', encoding='utf-8') as f:
    source = f.read()

funcs_to_copy = [
    'chat', 'chat_messages_api', 'edit_message', 'delete_message', 'ban_user',
    'reels_feed', 'reel_detail', 'toggle_reel_like', 'add_reel_comment', 'reel_comments_api', 'reel_share',
    'story_view', 'mark_story_seen', 'next_story_view', 'prev_story_view'
]

extracted = []

for func in funcs_to_copy:
    # Regex to capture the function definition until the next top-level def or end of file
    # This might capture some extra decorators, but mostly works.
    pattern = re.compile(r'^(?:@\w+\s*)*def ' + func + r'\(.*?(?=^@|^def |\Z)', re.MULTILINE | re.DOTALL)
    match = pattern.search(source)
    if match:
        extracted.append(match.group(0))
    else:
        print(f"Function {func} not found!")

# Now add necessary imports to anistream/anime/views.py if missing
with open('d:/anime/anistream/anime/views.py', 'r', encoding='utf-8') as f:
    dest = f.read()

missing_imports = """
from django.http import JsonResponse
from django.utils import timezone
from .models import ChatMessage, ReelLike, ReelComment, ReelShare, StoryView, Story, Reel
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
import json
"""

dest_top = missing_imports + "\n\n" + dest

new_code = dest_top + "\n\n# --- MIGRATED VIEWS ---\n\n" + "\n\n".join(extracted)

with open('d:/anime/anistream/anime/views.py', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Views migrated successfully.")
