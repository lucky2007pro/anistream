import re

with open(r'd:\AniDev\anime\templates\detail.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Genres
content = re.sub(
    r'<div class="genres">\s*<span>Action</span>\s*<span>Fantasy</span>\s*<span>{{ anime.release_year }}</span>\s*</div>',
    '''<div class="genres">\n            {% for genre in anime.genres.all %}\n            <span>{{ genre.name }}</span>\n            {% endfor %}\n            <span>{{ anime.release_year }}</span>\n        </div>''',
    content
)

# 2. Info Grid
info_grid_old = r'''            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Studiya</div>
                    <div class="info-value">A-1 Pictures</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Holati</div>
                    <div class="info-value" style="color: #00c853;">Davom etmoqda</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Yosh chegarasi</div>
                    <div class="info-value">16+</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Chiqarilgan yili</div>
                    <div class="info-value">{{ anime.release_year }}</div>
                </div>
            </div>'''
info_grid_new = '''            <div class="info-grid">
                <div class="info-card">
                    <div class="info-label">Studiya</div>
                    <div class="info-value">{{ anime.studio|default:"Noma'lum" }}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Holati</div>
                    <div class="info-value" style="color: #00c853;">{{ anime.get_status_display }}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Yosh chegarasi</div>
                    <div class="info-value">{{ anime.age_rating }}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Chiqarilgan yili</div>
                    <div class="info-value">{{ anime.release_year }}</div>
                </div>
            </div>'''
content = content.replace(info_grid_old, info_grid_new)

# 3. Duplicate Hamburger Menu
hamburger_css = '''        /* ===== HAMBURGER MENU ===== */
        .hamburger {
            display: none;
            flex-direction: column;
            gap: 5px;
            cursor: pointer;
            background: transparent;
            border: none;
            padding: 5px;
            z-index: 10001;
        }
        .hamburger span {
            display: block;
            width: 25px;
            height: 2px;
            background: #fff;
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        .hamburger.active span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
        .hamburger.active span:nth-child(2) { opacity: 0; }
        .hamburger.active span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

        .mobile-nav-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15,15,19,0.98);
            z-index: 10000;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 0;
        }
        .mobile-nav-overlay.open { display: flex; }
        .mobile-nav-overlay a {
            color: #fff;
            text-decoration: none;
            font-size: 1.4rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            padding: 18px 40px;
            width: 100%;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            transition: color 0.2s, background 0.2s;
        }
        .mobile-nav-overlay a:hover { color: #ff3366; background: rgba(255,51,102,0.05); }
        .mobile-nav-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            border: none;
            color: white;
            font-size: 1.8rem;
            cursor: pointer;
        }
'''
if content.count(hamburger_css) > 1:
    content = content.replace(hamburger_css, '', 1)

# 4. Simplify Player Overlay
start_idx = content.find('<div class="player-overlay" id="customPlayer">')
end_idx = content.find('</script>\\n\\n<script>\\n    function toggleMobileNav()')
if end_idx == -1:
    end_idx = content.find('</script>\\n\\n<script>\\n    function toggleMobileNav()'.replace('\\n', '\\n'))
if end_idx == -1:
    end_idx = content.find('</script>\n\n<script>\n    function toggleMobileNav()')


player_new = '''<div class="player-overlay" id="customPlayer">
        <div class="video-container" id="videoContainer">
            <div class="player-header" id="playerHeader">
                <div class="player-back" onclick="closePlayer()" style="background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 8px; cursor: pointer;">
                    <button class="player-back-icon" style="margin-right: 10px; background: none; color: white; border: none; font-size: 1.2rem; cursor: pointer;">❮</button>
                    <div class="player-title">
                        <h2 id="playerTitle" style="margin: 0; font-size: 1.1rem;">{{ anime.title }}</h2>
                    </div>
                </div>
                <button class="player-settings-btn" onclick="toggleEpisodes()" style="background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 8px; color: white; border: none; cursor: pointer;">📚 Qismlar</button>
            </div>

            <video id="mainVideo" controls preload="auto" playsinline style="width: 100%; height: 100%; max-height: 100vh; background: #000; outline: none;" crossorigin="anonymous"></video>

            <div id="playerStatusOverlay" class="player-status-overlay hidden">
                <div id="playerSpinner" class="player-spinner"></div>
                <div id="playerStatusText" class="player-status-text">Video yuklanmoqda...</div>
            </div>

            <div class="episodes-modal" id="episodesModal">
                <div class="ep-modal-header">
                    <h3>Qismlar ro'yxati <br><span style="font-size: 0.85rem; color: var(--text-dim); font-weight: normal;">"{{ anime.title }}"</span></h3>
                    <button class="player-settings-btn" style="width: 40px; height:40px; font-size: 1rem;" onclick="toggleEpisodes()">✕</button>
                </div>

                <div class="ep-list">
                    {% for ep in anime.episodes.all %}
                    <div class="ep-list-item" onclick="playEpisode('{{ ep.get_video_source|escapejs }}', '{{ ep.episode_number }}')">
                        <div class="ep-list-thumb"></div>
                        <div class="ep-list-info">
                            <h4>{{ ep.episode_number }}-qism</h4>
                            <span>{{ ep.title|default:"Yangi qism" }}</span> <span style="background: var(--accent); color: white; margin-left: 5px;">HD</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script>
        function openTab(tabId, element) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            element.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active-content'));
            document.getElementById(tabId).classList.add('active-content');
        }

        const banner = document.getElementById('parallaxBanner');
        window.addEventListener('scroll', () => {
            let scrollY = window.scrollY;
            if (scrollY < 800) {
                banner.style.transform = `translateY(${scrollY * 0.4}px) scale(${1 + scrollY * 0.0005})`;
            }
        });

        const playerOverlay = document.getElementById('customPlayer');
        const video = document.getElementById('mainVideo');
        const playerTitle = document.getElementById('playerTitle');
        const episodesModal = document.getElementById('episodesModal');
        const playerStatusOverlay = document.getElementById('playerStatusOverlay');
        const playerSpinner = document.getElementById('playerSpinner');
        const playerStatusText = document.getElementById('playerStatusText');

        function showPlayerStatus(text, showSpinner = true) {
            playerStatusText.textContent = text;
            playerStatusOverlay.classList.remove('hidden');
            if(playerSpinner) playerSpinner.classList.toggle('hidden', !showSpinner);
        }

        function hidePlayerStatus() {
            playerStatusOverlay.classList.add('hidden');
        }

        function playEpisode(videoSrc, epNum) {
            if (!videoSrc) {
                showPlayerStatus("Bu qism uchun video manbasi topilmadi.", false);
                playerOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
                return;
            }
            video.src = videoSrc;
            video.load();
            playerTitle.innerText = `{{ anime.title|escapejs }} - ${epNum}-qism`;
            playerOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            toggleEpisodes(false);
            
            showPlayerStatus("Video yuklanmoqda...", true);
            video.play().catch(e => {
                showPlayerStatus("Avtomatik boshlanish xatosi. Play tugmasini bosing.", false);
                hidePlayerStatus();
                console.error("Play error:", e);
            });
        }

        function playFirstEpisode() {
            {% if anime.episodes.first %}
                playEpisode('{{ anime.episodes.first.get_video_source|escapejs }}', '{{ anime.episodes.first.episode_number }}');
            {% else %}
                alert("Kechirasiz, hali bu animening qismlari bazaga qo'shilmagan!");
            {% endif %}
        }

        function closePlayer() {
            playerOverlay.classList.remove('active');
            video.pause();
            video.removeAttribute('src');
            video.load();
            document.body.style.overflow = 'auto';
            episodesModal.classList.remove('open');
            hidePlayerStatus();
        }

        function toggleEpisodes(force_state) {
            if (force_state !== undefined) {
                if (force_state) episodesModal.classList.add('open');
                else episodesModal.classList.remove('open');
            } else {
                episodesModal.classList.toggle('open');
            }
        }

        video.addEventListener('loadstart', () => showPlayerStatus("Video yuklanmoqda...", true));
        video.addEventListener('waiting', () => showPlayerStatus("Buffering...", true));
        video.addEventListener('canplay', hidePlayerStatus);
        video.addEventListener('playing', hidePlayerStatus);
        video.addEventListener('error', () => {
            showPlayerStatus("Video ijro etib bo'lmadi.", false);
        });
    </script>
'''

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + player_new + content[end_idx:]
else:
    print("Could not find start or end token")

with open(r'd:\AniDev\anime\templates\detail.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Success')
