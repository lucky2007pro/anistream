import os

filepath = r"d:\anime\anistream\anime\templates\home.html"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS
css_start = content.find("/* ----- HERO SLIDER ----- */")
css_end = content.find("/* ----- MAIN CONTENT ----- */")
if css_start != -1 and css_end != -1:
    new_css = """/* ----- HERO SLIDER ----- */
    .slider-wrapper-outer {
        width: 100%;
        margin: 0;
        padding: 0;
        max-width: 100%;
    }

    .slider-container {
        position: relative;
        width: 100%;
        aspect-ratio: auto;
        height: 65vh;
        min-height: 500px;
        max-height: 700px;
        overflow: hidden;
        border-radius: 0;
        margin: 0;
        box-shadow: none;
    }

    .slides-wrapper {
        display: flex;
        width: 100%;
        height: 100%;
        transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1);
        cursor: grab;
        user-select: none;
        will-change: transform;
    }
    .slides-wrapper.dragging { cursor: grabbing; transition: none; }

    .slide {
        min-width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        align-items: center;
        padding: 0 5%;
        overflow: hidden;
        flex-shrink: 0;
    }

    .slide-bg-blur {
        position: absolute;
        top: -10%; left: -10%;
        width: 120%; height: 120%;
        z-index: 1;
        overflow: hidden;
    }
    .slide-bg-blur img, .slide-bg-blur video {
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: blur(20px) brightness(0.4);
        transform: scale(1.1);
    }

    .slide-overlay-dark {
        position: absolute;
        inset: 0;
        z-index: 2;
        background: linear-gradient(to right, rgba(15,15,19,0.95) 0%, rgba(15,15,19,0.7) 50%, rgba(15,15,19,0.3) 100%),
                    linear-gradient(to top, rgba(15,15,19,1) 0%, transparent 40%);
    }

    .slide-content-split {
        position: relative;
        z-index: 10;
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        max-width: 1400px;
        margin: 0 auto;
        gap: 40px;
    }

    .slide-info-left {
        flex: 1;
        max-width: 650px;
    }

    .hero-badges {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
        flex-wrap: wrap;
    }

    .hero-badge-rating {
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
    }
    .hero-badge-episodes {
        background: rgba(0, 150, 255, 0.2);
        color: #00aaff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 800;
        border: 1px solid rgba(0, 150, 255, 0.4);
    }

    .slide-title {
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 15px;
        text-transform: uppercase;
        color: #fff;
        text-shadow: 0 4px 20px rgba(0,0,0,0.8);
        letter-spacing: -0.02em;
    }

    .hero-genres {
        display: flex;
        gap: 8px;
        margin-bottom: 18px;
        flex-wrap: wrap;
    }
    .hero-genres span {
        border: 1px solid rgba(255,255,255,0.2);
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #ddd;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .hero-desc {
        font-size: 0.95rem;
        line-height: 1.6;
        color: rgba(255,255,255,0.7);
        margin-bottom: 30px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .btn-play-yellow {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 14px 32px;
        border-radius: 8px;
        background: #ffc107;
        color: #000;
        font-size: 1rem;
        font-weight: 800;
        text-transform: uppercase;
        text-decoration: none;
        box-shadow: 0 0 20px rgba(255, 193, 7, 0.3);
        transition: all 0.3s ease;
    }
    .btn-play-yellow:hover {
        background: #ffca2c;
        transform: translateY(-3px);
        box-shadow: 0 0 30px rgba(255, 193, 7, 0.5);
    }

    .slide-poster-right {
        display: none;
    }

    .slider-controls {
        position: absolute;
        bottom: 30px;
        left: 5%;
        display: flex;
        gap: 8px;
        z-index: 20;
    }
    .dot {
        width: 28px;
        height: 3px;
        background: rgba(255,255,255,0.2);
        border-radius: 2px;
        cursor: pointer;
        transition: all 0.3s;
        border: none;
        padding: 0;
        outline: none;
    }
    .dot[aria-pressed="true"] {
        background: #ffc107;
        width: 46px;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.6);
    }

    @media (min-width: 900px) {
        .slide-poster-right {
            display: block;
            width: 300px;
            flex-shrink: 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 0 0 2px rgba(255,255,255,0.1), 0 20px 50px rgba(0,0,0,0.8);
            transform: perspective(1000px) rotateY(-8deg);
            transition: transform 0.5s ease;
            position: relative;
        }
        .slide-poster-right:hover {
            transform: perspective(1000px) rotateY(0deg) scale(1.03);
        }
        .slide-poster-right img {
            width: 100%;
            height: auto;
            aspect-ratio: 2 / 3;
            object-fit: cover;
            display: block;
        }
    }
    
    @media (max-width: 900px) {
        .slide-title { font-size: 2.5rem; }
    }
    @media (max-width: 480px) {
        .slider-container { height: 75vh; min-height: 450px; }
        .slide-content-split { align-items: flex-end; padding-bottom: 20px; }
        .slide-title { font-size: 2rem; }
        .hero-desc { -webkit-line-clamp: 4; }
        .btn-play-yellow { width: 100%; }
        .slider-controls { left: 50%; transform: translateX(-50%); bottom: 15px; }
    }

    """
    content = content[:css_start] + new_css + content[css_end:]
    
html_start = content.find("<!-- HERO SLIDER -->")
html_end = content.find("<!-- TAVSIYA ETILADIGANLAR -->")
if html_start != -1 and html_end != -1:
    new_html = """<!-- HERO SLIDER -->
    {% if hero_movies %}
    <div class="slider-wrapper-outer">
        <div class="slider-container" id="heroSlider">
            <div class="slides-wrapper" id="slidesWrapper">

                {% for anime in hero_movies %}
                {% if anime.id %}
                <div class="slide new-hero-layout">

                    <!-- Background Blur -->
                    <div class="slide-bg-blur">
                        {% if anime.hero_media and anime.hero_media.url|slice:"-4:" == ".mp4" or anime.hero_media and anime.hero_media.url|slice:"-4:" == "webm" %}
                            <video autoplay loop muted playsinline preload="metadata">
                                <source src="{{ anime.hero_media.url }}">
                            </video>
                        {% elif anime.hero_media %}
                            <img src="{{ anime.hero_media.url }}" alt="{{ anime.title }}" loading="eager">
                        {% else %}
                            <img src="{% if anime.image %}{{ anime.image.url }}{% else %}{{ default_movie_poster }}{% endif %}" alt="{{ anime.title }}" loading="eager">
                        {% endif %}
                    </div>

                    <div class="slide-overlay-dark"></div>

                    <!-- Content Split -->
                    <div class="slide-content-split">
                        
                        <!-- Left Info -->
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
                        </div>

                        <!-- Right Poster -->
                        <div class="slide-poster-right">
                            <img src="{% if anime.image %}{{ anime.image.url }}{% else %}{{ default_movie_poster }}{% endif %}" alt="{{ anime.title }}">
                        </div>

                    </div>

                    <div class="slider-controls">
                        {% for h_anime in hero_movies %}
                        {% if h_anime.id %}
                        <button class="dot dot-{{ forloop.counter0 }}"
                             aria-pressed="{% if forloop.parentloop.counter0 == forloop.counter0 %}true{% else %}false{% endif %}"
                             onclick="goToSlide({{ forloop.counter0 }})">
                        </button>
                        {% endif %}
                        {% endfor %}
                    </div>

                </div>
                {% endif %}
                {% endfor %}

            </div>
        </div>
    </div>
    {% endif %}

    """
    content = content[:html_start] + new_html + content[html_end:]

# also remove old media queries that overlap
# finding things like .slider-container in media max-width 768px etc.
# to prevent layout breaking, I'll just use simple regex or rely on the new CSS overriding
    
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated locally")
