import feedparser
import logging
from dateutil import parser
from django.conf import settings
from django.core.management.base import BaseCommand
from podcasts.models import Episode
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

logger = logging.getLogger(__name__)

def save_new_episodes(feed):
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries: ## loop to check if episode ID is within database, and if not, to add it
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.link,
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()

def fetch_realpython_episodes(): ## original feed
    _feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
    save_new_episodes(_feed)

def fetch_talkpython_episodes(): ## adding additional feed
    _feed = feedparser.parse("https://talkpython.fm/episodes/rss")
    save_new_episodes(_feed)

class Command(BaseCommand): # calling functions
    help = "Runs apscheduler." 

    ## create schedular instance, add job storage
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # schedular check for rp episodes
        scheduler.add_job(
            fetch_realpython_episodes,
            trigger="interval",
            minutes=2,
            id="The Real Python Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: The Real Python Podcast.")

        # schedular check for talk python episodes
        scheduler.add_job(
            fetch_talkpython_episodes,
            trigger="interval",
            minutes=2,
            id="Talk Python Feed",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Talk Python Feed.")

        # schedular task to delete old podcasts
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

## function to delete old podcasts based on age. here max age is seconds i.e. 1 week
def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
