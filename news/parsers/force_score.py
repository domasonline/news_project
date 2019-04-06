from news.models import NewsPost
from news.models import Source
from django_cron import CronJobBase, Schedule


class ForceScoreCron(CronJobBase):
    interval = 5000000000

    schedule = Schedule(run_every_mins=interval)
    code = 'news.general_parser_cron'

    def do(self):
        self.force_scores()

    @staticmethod
    def force_scores():
        posts = NewsPost.objects.all()
        for post in posts:
            post.simulated_score = 1000
            post.save()
