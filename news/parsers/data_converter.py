import json
from news.models import PostCategory
from news.models import Source
from django_cron import CronJobBase, Schedule
import os


class DataConverterCron(CronJobBase):
    interval = 12000

    schedule = Schedule(run_every_mins=12000)
    code = 'news.data_converter_cron'

    def do(self):
        self.data_converter()

    @staticmethod
    def data_converter():
        module_dir = os.path.dirname(__file__)
        source_path = os.path.join(module_dir, 'sources.json')
        cat_path = os.path.join(module_dir, 'categories.json')

        with open(source_path) as data_file:
            sources = json.load(data_file)
        with open(cat_path) as data_file:
            categories = json.load(data_file)

        for cat_id, vals in categories.items():
            category_name = vals.get('name')
            category_id = PostCategory.objects.filter(name=category_name)
            if not category_id:
                vals = {
                    'name': category_name,
                    'color': vals.get('color'),
                    'alt_img': vals.get('alt_img')
                }
                category_id = PostCategory(**vals)
                category_id.save()

        for source, vals in sources.items():
            category_name = vals.get('category')
            category_id = PostCategory.objects.get(name=category_name)
            source_code = vals.get('code')
            source_id = Source.objects.filter(code=source_code)
            if not source_id:
                vals = {
                    'code': source_code,
                    'name': vals.get('name'),
                    'rss': vals.get('rss'),
                    'category_id': category_id,
                    'link': vals.get('link'),
                }
                source_id = Source(**vals)
                source_id.save()
