from django.shortcuts import render, redirect
from news.models import NewsPost
from news.models import PostCategory
from news.models import PostVotes
import operator
from functools import reduce
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import ListView
import datetime
from dateutil.relativedelta import relativedelta
import json
from el_pagination.decorators import page_template
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.utils.timezone import make_aware


@page_template('news/posts.html')
def home(request, template='news/home.html', extra_context=None):
    get_data = request.GET.dict()
    view_mode = False
    time_filter = False
    if get_data:
        cat_ids = {}
        sort_by = False
        search_domain = ''
        for key, value in get_data.items():
            if 'categories' in key:
                number = int(json.loads(key.replace('categories', ''))[0])
                cat_ids[number] = value
            elif 'sort_by' in key:
                sort_by = get_data.get('sort_by')
            elif 'search_domain' in key:
                search_domain = get_data.get('search_domain')
            elif 'view_mode' in key:
                view_mode = get_data.get('view_mode')
            elif 'timestamp' in key:
                time_filter = get_data.get('timestamp')
        search_domain = json.loads(search_domain)
        if 'Block' in view_mode:
            view_mode = 'Block'
        sort_top = False
        sort_contr = False
        sort_rising = False
        if sort_by == 'Top Rated':
            sort_domain = ''
            sort_top = True
        elif sort_by == 'Controversial':
            sort_domain = ''
            sort_contr = True
        elif sort_by == 'Rising':
            sort_domain = ''
            sort_rising = True
        else:
            sort_domain = 'date'
        ids = []
        for key, value in cat_ids.items():
            if value == 'true':
                try:
                    ids.append(int(key))
                except ValueError:
                    ids.append(key)
        if 'all_categs' in ids:
            if sort_top:
                unsorted_results = NewsPost.objects.all()
                unsorted_results = sort_by_date(unsorted_results, time_filter)
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_votes_raw(), reverse=True)
            elif sort_contr:
                unsorted_results = NewsPost.objects.all()
                unsorted_results = sort_by_date(unsorted_results, time_filter)
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_votes_contr(), reverse=True)
            elif sort_rising:
                unsorted_results = NewsPost.objects.all()
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_rising_ratio(), reverse=True)
            else:
                data = NewsPost.objects.all().order_by('-'+sort_domain)
                data = sort_by_date(data, time_filter)
                data = search(data, search_domain)

        else:
            if sort_top:
                unsorted_results = NewsPost.objects.filter(category_id__id__in=ids)
                unsorted_results = sort_by_date(unsorted_results, time_filter)
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_votes_raw(), reverse=True)
            elif sort_contr:
                unsorted_results = NewsPost.objects.filter(category_id__id__in=ids)
                unsorted_results = sort_by_date(unsorted_results, time_filter)
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_votes_contr(), reverse=True)
            elif sort_rising:
                unsorted_results = NewsPost.objects.filter(category_id__id__in=ids)
                unsorted_results = search(unsorted_results, search_domain)
                data = sorted(unsorted_results, key=lambda t: t.get_rising_ratio(), reverse=True)
            else:
                data = NewsPost.objects.filter(category_id__id__in=ids).order_by('-'+sort_domain)
                data = sort_by_date(data, time_filter)
                data = search(data, search_domain)

        now = timezone.now()
        if view_mode == 'Block':
            it = iter(data)
            data = list(zip(it, it, it))
        context = {
            'data': data,
            'categories': PostCategory.objects.all(),
            'now': now,
            'view_mode': view_mode,
        }
        if extra_context is not None:
            context.update(extra_context)
        response = render(request, template, context)
        set_cookie(response, 'cat_ids', ids)
        setattr(request, 'view', 'news_main')
        return response
    else:
        data = NewsPost.objects.all().order_by('-date')
        now = timezone.now()
        if view_mode == 'Block':
            it = iter(data)
            data = list(zip(it, it, it))
        context = {
            'data': data,
            'categories': PostCategory.objects.all(),
            'now': now,
            'view_mode': view_mode,
        }
        if extra_context is not None:
            context.update(extra_context)
        setattr(request, 'view', 'news_main')
        return render(request, template, context)


def faq(request, template='news/faq.html'):
    return render(request, template)


def sort_by_date(data, time_filter):
    date = datetime.datetime.utcnow()
    date = make_aware(date)
    if time_filter == '24 Hours':
        date_start = date - relativedelta(hours=24)
        data = data.filter(date__range=(date_start, date))
    if time_filter == 'Week':
        date_start = date - relativedelta(days=7)
        data = data.filter(date__range=(date_start, date))
    if time_filter == 'Month':
        date_start = date - relativedelta(months=1)
        data = data.filter(date__range=(date_start, date))
    if time_filter == 'Year':
        date_start = date - relativedelta(years=1)
        data = data.filter(date__range=(date_start, date))
    return data


def search(data, search_domain):
    if search_domain:

        query = reduce(operator.and_, (Q(title__icontains=item) |
                                       Q(text__icontains=item) |
                                       Q(article_link__icontains=search_domain) for item in search_domain))

        data = data.filter(query)
    return data


@csrf_protect
def vote(request):
    data = request.GET.dict()
    user = request.user
    if data.get('upvote', False):
        post_id = data.get('upvote', False)

        post_vote = user.postvotes_set.filter(post_id=int(post_id))
        if not post_vote:
            entry = NewsPost.objects.get(pk=int(post_id))
            vals = {
                'user_id': user,
                'post_id': entry,
                'up_vote': 1,
            }
            vote_obj = PostVotes(**vals)
            vote_obj.save()
            return HttpResponse(1)
        else:
            post_vote = post_vote[0]
            if post_vote.down_vote and not post_vote.up_vote:
                post_vote.down_vote = 0
                post_vote.up_vote = 1
                post_vote.save()
                return HttpResponse(2)
            return HttpResponse(0)

    elif data.get('downvote', False):
        post_id = data.get('downvote', False)
        post_vote = user.postvotes_set.filter(post_id=int(post_id))
        if not post_vote:
            entry = NewsPost.objects.get(pk=int(post_id))
            vals = {
                'user_id': user,
                'post_id': entry,
                'down_vote': 1,
            }
            vote_obj = PostVotes(**vals)
            vote_obj.save()
            return HttpResponse(-1)
        else:
            post_vote = post_vote[0]
            if post_vote.up_vote and not post_vote.down_vote:
                post_vote.down_vote = 1
                post_vote.up_vote = 0
                post_vote.save()
                return HttpResponse(-2)
            return HttpResponse(0)


class PostListView(ListView):
    model = NewsPost


def about(request):
    setattr(request, 'view', 'news_main')
    return render(request, 'news/about.html')


def set_cookie(response, key, value, days_expire=60):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires)


