from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware


class PostCategory(models.Model):

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100, default='red')
    alt_img = models.CharField(max_length=50, default='alt')

    def __str__(self):
        return self.name


class Source(models.Model):

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=150)
    rss = models.CharField(max_length=250)
    category_id = models.ForeignKey(PostCategory, on_delete=models.CASCADE, blank=True, null=True)
    score = models.IntegerField(default=0)
    link = models.CharField(max_length=150)

    def __str__(self):
        return self.code


class NewsPost(models.Model):

    title = models.CharField(max_length=250, default='')
    ext_id = models.CharField(max_length=250, default='ext_id')
    text = models.TextField(default='Article text')
    date = models.DateTimeField()
    image_scr = models.CharField(max_length=100)
    article_link = models.CharField(max_length=100)
    category_id = models.ForeignKey(PostCategory, on_delete=models.CASCADE, blank=True, null=True)
    source_id = models.ForeignKey(Source, on_delete=models.SET_NULL, blank=True, null=True)
    simulated_score = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_display_title(self):
        return self.title[0:60] + '...' if len(self.title) > 60 else self.title

    def get_display_text(self):
        if self.text:
            return self.text[0:150] + '...' if len(self.text) > 150 else self.text
        else:
            return self.title[0:150] + '...' if len(self.title) > 150 else self.title

    def get_scr(self):
        if self.image_scr:
            return self.image_scr
        else:
            return '/../../static/news/maxresdefault.jpg'

    def get_votes(self):
        up_votes = 0
        down_votes = 0
        for obj in self.postvotes_set.all():
            if obj.down_vote:
                down_votes += 1
            elif obj.up_vote:
                up_votes += 1
        total = up_votes - down_votes + self.simulated_score
        total_abs = abs(total)
        if total_abs >= 1000:
            represent = total / 1000
            if represent.is_integer():
                represent = int(represent)
            return str(represent) + 'k'
        else:
            return total

    def get_votes_raw(self):
        up_votes = 0
        down_votes = 0
        for obj in self.postvotes_set.all():
            if obj.down_vote:
                down_votes += 1
            elif obj.up_vote:
                up_votes += 1
        total = up_votes - down_votes + self.simulated_score
        return total

    def get_votes_contr(self):
        up_votes = 0
        down_votes = 0
        for obj in self.postvotes_set.all():
            if obj.down_vote:
                down_votes += 1
            elif obj.up_vote:
                up_votes += 1
        total = abs(up_votes) + abs(down_votes) + self.simulated_score
        return total

    def get_post_vote_color(self, user):
        vote = self.postvotes_set.filter(user_id=user)
        if vote:
            vote = vote[0]
            if vote.up_vote:
                return 'green'
            else:
                return 'red'
        else:
            return 'black'

    def get_rising_ratio(self):
        date = datetime.utcnow()
        date = make_aware(date)
        down_votes = up_votes = 0
        votes = self.postvotes_set.all()
        date_start = date - relativedelta(hours=24)
        votes = votes.filter(vote_time__range=(date_start, date))

        for obj in votes:
            if obj.down_vote:
                down_votes += 1
            elif obj.up_vote:
                up_votes += 1
        total = up_votes - down_votes
        return total


class Comment(models.Model):

    text = models.TextField()
    comment_date = models.DateTimeField(default=timezone.now)


class PostVotes(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=User.objects.filter(username__in='admin'))
    post_id = models.ForeignKey(NewsPost, on_delete=models.CASCADE, default='')
    up_vote = models.IntegerField(default=0)
    down_vote = models.IntegerField(default=0)
    vote_time = models.DateTimeField(auto_now_add=True)




