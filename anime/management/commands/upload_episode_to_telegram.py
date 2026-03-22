from django.core.management.base import BaseCommand, CommandError

from anime.models import Episode
from anime.services.telegram_storage import TelegramStorageError, upload_episode_to_telegram


class Command(BaseCommand):
    help = "Episode video_file'ni Telegram kanalga yuklaydi va file_id saqlaydi"

    def add_arguments(self, parser):
        parser.add_argument("episode_id", type=int, help="Episode ID")
        parser.add_argument(
            "--delete-local",
            action="store_true",
            help="Telegram uploaddan keyin local video_file ni o'chirish",
        )

    def handle(self, *args, **options):
        episode_id = options["episode_id"]
        delete_local = options["delete_local"]

        try:
            episode = Episode.objects.select_related("anime").get(id=episode_id)
        except Episode.DoesNotExist as exc:
            raise CommandError(f"Episode topilmadi: {episode_id}") from exc

        try:
            last_percent = {"value": -1}

            def _progress(uploaded, total):
                if total <= 0:
                    return
                percent = int((uploaded * 100) / total)
                if percent > last_percent["value"]:
                    last_percent["value"] = percent
                    self.stdout.write(f"Upload: {percent}%")

            upload_episode_to_telegram(
                episode,
                delete_local_file=delete_local,
                progress_callback=_progress,
            )
        except TelegramStorageError as exc:
            raise CommandError(f"Telegram upload xato: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(
            f"Yuklandi: {episode.anime.title} {episode.episode_number}-qism | file_id={episode.telegram_file_id}"
        ))

