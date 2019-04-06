import feedparser as fp
from newspaper import Article
from time import mktime
from django.utils import timezone
from datetime import datetime
from news.models import NewsPost
from news.models import Source
from django_cron import CronJobBase, Schedule


class GeneralParserCron(CronJobBase):
    interval = 2

    schedule = Schedule(run_every_mins=interval)
    code = 'news.general_parser_cron'

    def do(self):
        self.general_parser()

    @staticmethod
    def general_parser():
        limit = 10

        sources = Source.objects.all()
        for source in sources:
            feed = fp.parse(source.rss)
            count = 1
            for entry in feed.entries:
                if hasattr(entry, 'published'):
                    try:
                        post = NewsPost.objects.filter(ext_id=entry.id)
                        if post:
                            continue
                    except AttributeError:
                        continue
                    if count > limit:
                        break
                    date = entry.published_parsed if entry.published_parsed is not None else entry.published
                    date_formatted = datetime.fromtimestamp(mktime(date))
                    date_formatted = timezone.make_aware(date_formatted, timezone.get_current_timezone())

                    try:
                        try:
                            image_scr = entry.media_thumbnail[0].get('url', False)
                        except AttributeError:
                            image_scr = entry.media_content[0].get('url', False)
                    except AttributeError:
                        image_scr = False
                    if not image_scr:
                        print(image_scr, source.code)
                    try:
                        content = Article(entry.link)
                        content.download()
                        content.parse()
                    except Exception as e:
                        print(e)
                        continue

                    vals = {
                        'title': content.title,
                        'text': content.text,
                        'date': date_formatted,
                        'image_scr': image_scr,
                        'article_link': entry.link,
                        'ext_id': entry.id,
                        'category_id': source.category_id,
                        'source_id': source
                    }
                    post = NewsPost(**vals)
                    post.save()
                    count = count + 1



    #     count = 1
    #     for company, value in companies.items():
    #         if 'rss' in value:
    #             d = fp.parse(value['rss'])
    #             news_paper = {
    #                 "rss": value['rss'],
    #                 "link": value['link'],
    #                 "articles": []
    #             }
    #             for entry in d.entries:
    #                 if hasattr(entry, 'published'):
    #                     if count > limit:
    #                         break
    #                     date = entry.published_parsed if entry.published_parsed is not None else entry.published
    #                     if entry.media_thumbnail:
    #                         image_scr = entry.media_thumbnail[0].get('url', False)
    #                     else:
    #                         image_scr = False
    #                     article = {
    #                         'link': entry.link,
    #                         'published': '2019-01-01', # datetime.fromtimestamp(mktime(date)).isoformat()
    #                         'image_scr': image_scr
    #                     }
    #                     try:
    #                         content = Article(entry.link)
    #                         content.download()
    #                         content.parse()
    #                     except Exception as e:
    #                         print(e)
    #                         continue
    #                     article['title'] = content.title
    #                     article['text'] = content.text
    #                     news_paper['articles'].append(article)
    #                     category_name = value['category']
    #                     category_id = PostCategory.objects.get(name=category_name)
    #                     if not category_id:
    #                         vals = {
    #                             'name': category_name
    #                         }
    #                         category_id = PostCategory(**vals)
    #                         category_id.save()
    #
    #                     vals = {
    #                         'title': article.get('title'),
    #                         'text': article.get('text'),
    #                         'date': article.get('published'),
    #                         'source': value.get('link'),
    #                         'image_scr': article.get('image_scr'),
    #                         'article_link': article.get('link'),
    #                         'source_name': value.get('name'),
    #                     }
    #                     post = NewsPost(**vals)
    #                     post.category_id = category_id
    #                     post.save()
    #                     count = count + 1
    #
    #         # else:
    #         #     paper = newspaper.build(value['link'], memoize_articles=False)
    #         #     newsPaper = {
    #         #         "link": value['link'],
    #         #         "articles": []
    #         #     }
    #         #     noneTypeCount = 0
    #         #     for content in paper.articles:
    #         #         if count > limit:
    #         #             break
    #         #         try:
    #         #             content.download()
    #         #             content.parse()
    #         #         except Exception as e:
    #         #             print(e)
    #         #             print("continuing...")
    #         #             continue
    #         #         if content.publish_date is None:
    #         #             print(count, " Article has date of type None...")
    #         #             noneTypeCount = noneTypeCount + 1
    #         #             if noneTypeCount > 10:
    #         #                 print("Too many noneType dates, aborting...")
    #         #                 noneTypeCount = 0
    #         #                 break
    #         #             count = count + 1
    #         #             continue
    #         #         article = {}
    #         #         article['title'] = content.title
    #         #         article['text'] = content.text
    #         #         article['link'] = content.url
    #         #         article['published'] = '2019-01-01'
    #         #         newsPaper['articles'].append(article)
    #         #         print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
    #         #         count = count + 1
    #         #         noneTypeCount = 0
    #
    # def keyword_mapper(self, article):
    #     words = article.split(' ')



