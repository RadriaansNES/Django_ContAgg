import feedparser
from dateutil import parser
from django.core.management.base import BaseCommand
from podcasts.models import Episode

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
    def handle(self, *args, **options):
        fetch_realpython_episodes()
        fetch_talkpython_episodes()