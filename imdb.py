#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import collections
import argparse
import random
from bs4 import BeautifulSoup
import requests
from bottle import route, run, template, static_file, error
import urllib
import simplejson


def parse_csv_films(filename):
    films = []
    reader = csv.DictReader(
        open(filename),
        fieldnames=['movie id', 'movie title', 'release date',
                    'video release date', 'IMDb URL,unknown', 'Action',
                    'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime',
                    'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
                    'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                    'Thriller', 'War', 'Western'], delimiter='|')
    for row in reader:
        films.append(row)
    return films


def search(text):
    query = urllib.urlencode({'q': text.encode("utf-8")})
    url = u'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s'.encode("utf-8") % query
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    try:
        results = json['responseData']['results']
    except:
        results = 'Google api error'
    return results


def counting_by_year_genge(films, film_genre, film_year):
    counter_by_year_genge = collections.Counter()
    for film in films:
        counter_by_year_genge[film['release date'][-4:], film[film_genre]] += 1
    return counter_by_year_genge[(film_year, '1')]


def return_random_film_year_genre(films, film_genre, film_year):
    film_titles = []
    for film in films:
        if film['release date'][-4:] == film_year and film[film_genre] == '1':
            film_titles.append(dict(title=film['movie title'], link=film['IMDb URL,unknown']))
    return film_titles[random.randint(0, len(film_titles) - 1)]


def get_film_rate(url):
    doc = requests.get(url).text.encode('utf-8')
    soup = BeautifulSoup(doc, "html.parser")
    return soup.find('div', 'titlePageSprite star-box-giga-star').string


def get_image(url, img_path):
    doc = requests.get(url).text.encode('utf-8')
    soup = BeautifulSoup(doc, "html.parser")
    search_img = soup.find('div', 'image')
    img_link = str(search_img)[
               str(search_img).find('src=') + 5:str(search_img).find('"', str(search_img).find('src=') + 6)]
    load_img = requests.get(img_link)
    out = open(img_path, "wb")
    out.write(load_img.content)
    out.close()


@route('/movies/<genre>/<year>')
def index(genre, year):
    count_films_year = '{0} in {1} year: {2}'.format(
        genre, year, counting_by_year_genge(
            parse_csv_films('movies.csv'), genre, year))
    recommended_film = return_random_film_year_genre(
        parse_csv_films('movies.csv'), genre, year)
    title = 'Recommended film title: {0}'.format(recommended_film['title'])
    try:
        rating = 'Rating : {0}'.format(get_film_rate(recommended_film['link']))
        get_image(recommended_film['link'], "img.jpg")
        wiki_res = search("wiki " + recommended_film['title'])
        if wiki_res == 'Google api error':
            wiki = 'Wiki: Google api error'
        else:
            wiki = "Wiki: " + search(
                "wiki " + recommended_film['title'])[0]['url']
    except:
        results = search("imdb" + recommended_film['title'])
        if results == 'Google api error':
            rating = 'Google api error'
            wiki = 'Wiki: Google api error'
        else:
            url = results[0]['url']
            print(url)
            if 'imdb' in url:
                rating = 'Rating : {0}'.format(get_film_rate(url))
                get_image(url, "img.jpg")
                wiki_res = search("wiki " + recommended_film['title'])
                if wiki_res == 'Google api error':
                    wiki = 'Wiki: Google api error'
                else:
                    wiki = search(
                        "wiki " + recommended_film['title'])[0]['url']
            else:
                rating = 'Rating: google api and url in csv error'
                wiki = 'Wiki: Google api error'

    return template(
        'template', count_films_year=count_films_year,
        title=title, rating=rating, wiki=wiki)


# конроллер возвращает картинку, сохраненную при поиске
@route('/static/<path>')
def server_static(path):
    return static_file(path, root='')


@error(404)
@error(403)
def mistake(code):
    return 'Error on page'


if __name__ == '__main__':
    run(host='localhost', port=8080)
