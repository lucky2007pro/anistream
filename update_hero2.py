import os
import re

filepath = r"d:\anime\anistream\anime\templates\home.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace HTML structure
old_left_info = """<!-- Left Info -->
                        <div class="slide-info-left">
                            <div class="hero-badges">
                                {% if anime.rating %}
                                <span class="hero-badge-rating"><i class='bx bxs-star'></i> {{ anime.rating }}</span>
                                {% endif %}
                                {% if anime.episodes.count > 0 %}
                                <span class="hero-badge-episodes">{{ anime.episodes.count }} qism</span>
                                {% endif %}
                            </div>

                            <h1 class="slide-title">{{ anime.title }}</h1>

                            <div class="hero-genres">
                                {% if anime.category %}
                                <span>{{ anime.category.name }}</span>
                                {% endif %}
                                {% if anime.release_year %}
                                <span>YIL: {{ anime.release_year }}</span>
                                {% endif %}
                            </div>

                            {% if anime.description %}
                            <p class="hero-desc">{{ anime.description }}</p>
                            {% else %}
                            <p class="hero-desc">Yangi anime - {{ anime.title }}! Hozircha tavsif kiritilmagan. Lekin eng qiziqarli voqealar sizni kutmoqda.</p>
                            {% endif %}

                            <a href="{% url 'movie_detail' anime.id %}" class="btn-play-yellow">
                                <i class='bx bx-play'></i> TOMOSHA QILISH
                            </a>
                        </div>"""

new_left_info = """<!-- Left Info -->
                        <div class="slide-info-left">
                            <div class="hero-badges">
                                <span class="hero-badge-yangi">YANGI</span>
                                {% if anime.release_year %}
                                <span class="hero-badge-year">{{ anime.release_year }}</span>
                                {% endif %}
                                {% if anime.episodes.count > 0 %}
                                <span class="hero-badge-episodes">{{ anime.episodes.count }} qism</span>
                                {% endif %}
                            </div>

                            <h1 class="slide-title">{{ anime.title }}</h1>

                            <div class="hero-views">
                                <i class='bx bx-show'></i> {{ anime.views_count|default:"0" }}
                            </div>

                            <a href="{% url 'movie_detail' anime.id %}" class="btn-play-pink">
                                <i class='bx bx-play'></i> Hozir ko'rish
                            </a>
                        </div>"""

if old_left_info in content:
    content = content.replace(old_left_info, new_left_info)
    print("Replaced HTML")
else:
    print("Could not find old HTML")

# Replace CSS
old_css_part1 = """.hero-badge-rating {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 5px;
        border: 1px solid rgba(255, 193, 7, 0.4);
    }"""
new_css_part1 = """.hero-badge-yangi {
        background: rgba(0, 229, 255, 0.1);
        color: #00e5ff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 5px;
        border: 1px solid rgba(0, 229, 255, 0.4);
    }
    .hero-badge-year {
        background: rgba(255, 255, 255, 0.05);
        color: #e0e0e0;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 5px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .hero-views {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .hero-views i {
        color: #00e5ff;
        font-size: 1.2rem;
    }"""
content = content.replace(old_css_part1, new_css_part1)

# Replace btn-play-yellow CSS
content = re.sub(r'\.btn-play-yellow \{[^}]+\}', """.btn-play-pink {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 14px 32px;
        border-radius: 12px;
        background: linear-gradient(135deg, #ff003c, #ff4d6d);
        color: #fff;
        font-size: 1.1rem;
        font-weight: 800;
        text-decoration: none;
        box-shadow: 0 0 20px rgba(255, 51, 102, 0.3);
        transition: all 0.3s ease;
    }""", content)
content = re.sub(r'\.btn-play-yellow:hover \{[^}]+\}', """.btn-play-pink:hover {
        background: linear-gradient(135deg, #e00035, #e04461);
        transform: translateY(-3px);
        box-shadow: 0 0 30px rgba(255, 51, 102, 0.5);
    }""", content)

# Replace active dot color
content = content.replace("background: #ffc107;", "background: #00e5ff;")
content = content.replace("box-shadow: 0 0 10px rgba(255, 193, 7, 0.6);", "box-shadow: 0 0 10px rgba(0, 229, 255, 0.6);")

# Remove hero-genres CSS
content = re.sub(r'\.hero-genres \{[^}]+\}', '', content)
content = re.sub(r'\.hero-genres span \{[^}]+\}', '', content)
content = re.sub(r'\.hero-desc \{[^}]+\}', '', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("CSS updated locally")
