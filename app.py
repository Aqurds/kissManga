from flask import Flask, render_template, url_for, request, session, redirect, abort
from flask_pymongo import PyMongo, pymongo
import bcrypt
import json

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mangastuff'
app.config['MONGO_URI'] = 'mongodb://user:2252010baby@ds159785-a0.mlab.com:59785,ds159785-a1.mlab.com:59785/mangastuff?replicaSet=rs-ds159785'
app.config['SECRET_KEY'] = '0f9dc56d2288afa6e10b8d97577fe25b'


mongo = PyMongo(app)




# home/index route
@app.route('/')
def home():
    #new manga list
    new_manga = list(mongo.db.all_manga_details.find().sort('votes', pymongo.ASCENDING).limit(10))

    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))

    #latest manga view
    latest_front_page_manga = list(mongo.db.update_spider.find())
    latest_mange_releases = []
    for item in latest_front_page_manga[0]['latest_mange_releases']:
        latest_mange_releases.append(mongo.db.all_manga_details.find_one({'id':item}))

    latest_manga_releases_chapter_list = []
    for item in latest_front_page_manga[0]['latest_mange_releases']:
        latest_manga_releases_chapter_list.append(mongo.db.manga_chapter_list.find_one({'manga_id':item}))


    #most popular manga view
    most_popular_front_page_manga = list(mongo.db.update_spider.find())
    most_popular_manga = []

    for item in most_popular_front_page_manga[0]['most_popular_manga']:
        most_popular_manga.append(mongo.db.all_manga_details.find_one({'id':item}))

    genres_categories = list(mongo.db.genres_categories.find())
    genres = genres_categories[0]['genres']
    categories = genres_categories[0]['categories']

    total_bookmark = 0
    if session:
        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})


        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1

    # with open('test.html', 'w+') as outfile:
    #     json.dump(most_popular_manga, outfile)

    return render_template('index.html', mangas = front_page_manga, popular_manga_list=popular_manga_list, latest_mange_releases=latest_mange_releases, most_popular_manga=most_popular_manga, genres=genres, categories=categories, total_bookmark=total_bookmark, latest_manga_releases_chapter_list=latest_manga_releases_chapter_list, new_manga=new_manga)












if __name__ == '__main__':
    app.run(debug=True)
