from flask import Flask, render_template, url_for, request, session, redirect, abort, send_from_directory
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






# Main manga page with pagintion. Used in all types of manga page
@app.route('/manga/')
def manga():
    items = mongo.db.all_manga_details

    #Getting total manga number
    total_manga = len(list(items.find()))

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here

    page_offset = (current_page-1) * 24
    limit = 24

    starting_manga_id = items.find().sort('_id', pymongo.ASCENDING)
    last_manga_id = starting_manga_id[page_offset]['_id']

    # all_manga = list(items.find().limit(offset))
    all_manga = list(items.find({'_id':{'$gte':last_manga_id}}).sort('_id', pymongo.ASCENDING).limit(limit))


    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))



    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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


    return render_template('manga.html', all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)









@app.route('/manga-completed/')
def manga_completed():
    items = mongo.db.all_manga_details


    completed_manga_list = []

    for item in list(items.find()):
        if item['status'] == "Completed":
            completed_manga_list.append(item)

    page_offset = (int(request.args['page'])-1) * 24
    limit = 24 * int(request.args['page'])
    all_manga = completed_manga_list[page_offset:limit]


    #Getting total manga number
    total_manga = len(completed_manga_list)

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here



    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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

    return render_template('manga-completed.html', all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)









@app.route('/manga-new/')
def manga_new():
    items = mongo.db.all_manga_details

    #Getting total manga number
    total_manga = len(list(items.find()))

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here

    page_offset = (current_page-1) * 24
    limit = 24

    starting_manga_id = items.find().sort('votes', pymongo.ASCENDING)
    last_manga_id = starting_manga_id[page_offset]['_id']

    # all_manga = list(items.find().limit(offset))
    all_manga = list(items.find({'_id':{'$gte':last_manga_id}}).sort('votes', pymongo.ASCENDING).limit(limit))


    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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

    return render_template('manga-new.html', all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)









@app.route('/manga-hot/')
def manga_hot():
    items = mongo.db.all_manga_details

    #Getting total manga number
    total_manga = len(list(items.find()))

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here

    page_offset = (current_page-1) * 24
    limit = 24

    starting_manga_id = items.find().sort('votes', pymongo.DESCENDING)
    last_manga_id = starting_manga_id[page_offset]['_id']

    # all_manga = list(items.find().limit(offset))
    all_manga = list(items.find({'_id':{'$gte':last_manga_id}}).sort('votes', pymongo.DESCENDING).limit(limit))

    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))


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

    return render_template('manga-hot.html', all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)











@app.route('/manga-genre-search/')
def manga_genre_search():
    items = mongo.db.all_manga_details

    genre_id = request.args['genre']
    genres_manga_list = []

    for item in list(items.find()):
        if genre_id in item['genres']:
            genres_manga_list.append(item)

    page_offset = (int(request.args['page'])-1) * 24
    limit = 24 * int(request.args['page'])
    all_manga = genres_manga_list[page_offset:limit]


    #Getting total manga number
    total_manga = len(genres_manga_list)

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))


    genres_categories = list(mongo.db.genres_categories.find())
    genres = genres_categories[0]['genres']
    categories = genres_categories[0]['categories']

    #counting bookmark number to show in menu
    total_bookmark = 0
    if session:
        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})

        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1

    return render_template('manga-genre-search.html', genre_id=genre_id, all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark)











@app.route('/manga-author-search/')
def manga_author_search():
    items = mongo.db.all_manga_details
    author_id = request.args['author']

    author_manga_list = []

    for item in list(items.find()):
        if author_id in item['author']:
            author_manga_list.append(item)

    all_manga = author_manga_list


    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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

    return render_template('manga-author-search.html', all_manga=all_manga, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)





@app.route('/account/')
def account():
    if session:

        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})

        total_bookmark = 0
        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1
        return render_template('account.html', total_bookmark=total_bookmark)
    else:
        return redirect(url_for('login'))





@app.route('/manga-id-chapter/<string:manga_id>/<string:chapter_id>')
def manga_id_chapter(manga_id, chapter_id):
    manga_id =manga_id
    chapter_id = chapter_id
    url = request.url
    manga_details = mongo.db.all_manga_details.find_one({'id':manga_id})
    manga_chapter_list = mongo.db.manga_chapter_list.find_one({'manga_id':manga_id})
    chapter_list = list(mongo.db.manga_each_chapter_image_list_with_manga_id.find({'manga_id':manga_id}))

    index = manga_chapter_list['chapter_id'].index(chapter_id)
    image_list = chapter_list[index]['manga_each_chapter_image_list_with_manga_id']
    current_chapter_text = manga_chapter_list['chapter_link_text'][index]

    current_chapter_id = chapter_id
    if index == len(manga_chapter_list['chapter_id'])-1:
        prev_chapter_id = manga_chapter_list['chapter_id'][1 + 1]
    else:
        prev_chapter_id = manga_chapter_list['chapter_id'][index + 1]
    next_chapter_id = manga_chapter_list['chapter_id'][index - 1]
    next_chapter_identifier = True
    prev_chapter_id_identifier = True

    if current_chapter_id == manga_chapter_list['chapter_id'][0]:
        next_chapter_identifier = False

    if current_chapter_id == manga_chapter_list['chapter_id'][-1]:
        prev_chapter_id_identifier = False

    iteration_number = len(manga_chapter_list['chapter_id'])
    chapter_option_list = []
    for y in range(iteration_number):
        chapter_option_list.append([manga_chapter_list['chapter_id'][y]])
    for y in range(iteration_number):
        chapter_option_list[y].append(manga_chapter_list['chapter_link_text'][y])

    related_manga = mongo.db.all_manga_details.find().sort('last_updated', pymongo.ASCENDING).limit(12)


    total_bookmark = 0
    if session:
        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})

        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1

    return render_template('manga-id-chapter.html', manga_details = manga_details, manga_chapter_list = manga_chapter_list, image_list = image_list, url = url, current_chapter_id = current_chapter_text, prev_chapter_id = prev_chapter_id, next_chapter_id = next_chapter_id, next_chapter_identifier=next_chapter_identifier, prev_chapter_id_identifier=prev_chapter_id_identifier, chapter_option_list=chapter_option_list, related_manga=related_manga, total_bookmark=total_bookmark)










@app.route('/menu-search/', methods=['POST', 'GET'])
def menu_search():
    items = mongo.db.all_manga_details

    manga_chapter_list_from_paginated_manga = []


    search_manga_list = []
    search_term = request.form['searchtext']

    #manga search code
    if request.form['search_select'] == "Manga Name":
        #do text search
        initial_query_text = request.form['searchtext'].split()

        if len(initial_query_text) > 1:
            #do search with multi words
            search_text = request.form['searchtext'].title()

            for item in list(items.find()):
                if search_text in item['title'].title():
                    search_manga_list.append(item)


        if len(initial_query_text) == 1:
            #do single word search
            search_text = request.form['searchtext'].capitalize()

            for item in list(items.find()):
                title_name_list = item['title'].title().split()
                if search_text in title_name_list:
                    search_manga_list.append(item)


        for item in search_manga_list:
            manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #author search code
    if request.form['search_select'] == "Authors":
        #do author search
        author_text = request.form['searchtext'].lower()

        for item in list(items.find()):
            for autnor_name in item['author']:
                if author_text == autnor_name.lower():
                    search_manga_list.append(item)

        for item in search_manga_list:
            manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))



    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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


    return render_template('menu-search.html', popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, search_manga_list=search_manga_list, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga, search_term=search_term)










@app.route('/bookmark/')
def bookmark():

    if session:
        #popular manga view
        front_page_manga = list(mongo.db.update_spider.find())
        popular_manga_list = []

        for item in front_page_manga[0]['popular_manga']:
            # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
            popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))


        #most popular manga view
        most_popular_front_page_manga = list(mongo.db.update_spider.find())
        most_popular_manga = []

        for item in most_popular_front_page_manga[0]['most_popular_manga']:
            most_popular_manga.append(mongo.db.all_manga_details.find_one({'id':item}))

        genres_categories = list(mongo.db.genres_categories.find())
        genres = genres_categories[0]['genres']
        categories = genres_categories[0]['categories']


        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})
        # history = {'history':manga_id}
        # users.update({ "name":username },{$set : {"history":manga_id}})
        # users.insert_one(history)
        bookmark_data = []
        total_bookmark = 0
        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1
            for bookmark_manga in bookmark_id['bookmark']:
                bookmark_data.append(mongo.db.all_manga_details.find_one({'id':bookmark_manga}))

        if bookmark_data:
            bookmark_data.pop(0)


        return render_template('bookmark.html', popular_manga_list=popular_manga_list, most_popular_manga=most_popular_manga, genres=genres, categories=categories, bookmark_data=bookmark_data, total_bookmark=total_bookmark)
    else:
        return redirect(url_for('login'))









# add bookmark route
@app.route('/add-bookmark/<string:manga_id>')
def add_bookmark(manga_id):


    if session:
        manga_id = request.url.split('/')[-1]
        #store the manga id in users document for history page
        user_name = session['username']
        users = mongo.db.users
        bookmark_data = users.find_one({'name':user_name})

        if 'bookmark' not in bookmark_data:
            users.update_one({'name': user_name}, {'$push': {'bookmark':''}})

        bookmark_data_again = users.find_one({'name':user_name})
        if manga_id not in bookmark_data_again['bookmark']:
            users.update_one({'name': user_name}, {'$push': {'bookmark': manga_id}})

        return redirect(url_for('bookmark'))
    else:
        return redirect(url_for('login'))









@app.route('/manga-id/<string:manga_id>')
def manga_id(manga_id):
    # manga_id = request.url.split('/')[-1]
    manga_id = manga_id
    manga_details = mongo.db.all_manga_details.find_one({'id':manga_id})
    manga_chapter_list = mongo.db.manga_chapter_list.find_one({'manga_id':manga_id})

    # collecting each manga details in a single list with iteration. This code looking pretty complex. I will try to optimize this code later.
    manga_id_here = manga_chapter_list['manga_id']
    iteration = len(manga_chapter_list['chapter_id'])
    chapter_list = []
    for x in range(iteration):
        chapter_list.append([manga_chapter_list['chapter_id'][x]])

    for x in range(iteration):
        chapter_list[x].append(manga_chapter_list['full_chapter_url'][x])

    for x in range(iteration):
        chapter_list[x].append(manga_chapter_list['chapter_link_text'][x])

    for x in range(iteration):
        chapter_list[x].append(manga_chapter_list['chapter_time_uploaded'][x])

    #store the manga id in users document for history page
    if session:
        user_name = session['username']
        users = mongo.db.users
        history_data = users.find_one({'name':user_name})

        if 'history' not in history_data:
            users.update_one({'name': user_name}, {'$push': {'history':''}})

        history_data_again = users.find_one({'name':user_name})
        if manga_id not in history_data_again['history']:
            users.update_one({'name': user_name}, {'$push': {'history': manga_id}})


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))


    #most popular manga view
    most_popular_front_page_manga = list(mongo.db.update_spider.find())
    most_popular_manga = []

    for item in most_popular_front_page_manga[0]['most_popular_manga']:
        most_popular_manga.append(mongo.db.all_manga_details.find_one({'id':item}))

    # genres & categories to show in sidebar
    genres_categories = list(mongo.db.genres_categories.find())
    genres = genres_categories[0]['genres']
    categories = genres_categories[0]['categories']

    # counting bookmark number to show in the menu
    total_bookmark = 0
    if session:
        user_name = session['username']
        users = mongo.db.users
        bookmark_id = users.find_one({'name':user_name})

        if 'bookmark' in bookmark_id:
            total_bookmark = len(bookmark_id['bookmark']) - 1

    return render_template('manga-id.html', manga_details = manga_details, chapter_list = chapter_list, manga_id_here = manga_id_here, popular_manga_list=popular_manga_list, most_popular_manga=most_popular_manga, genres=genres, categories=categories, total_bookmark=total_bookmark)








@app.route('/manga-ongoing/')
def manga_ongoing():
    items = mongo.db.all_manga_details


    ongoing_manga_list = []

    for item in list(items.find()):
        if item['status'] == "Ongoing":
            ongoing_manga_list.append(item)

    page_offset = (int(request.args['page'])-1) * 24
    limit = 24 * int(request.args['page'])
    all_manga = ongoing_manga_list[page_offset:limit]


    #Getting total manga number
    total_manga = len(ongoing_manga_list)

    #getting total page number
    offset = 24
    page_number = total_manga / offset
    if total_manga % offset == 0:
        total_page_number = int(str(page_number).split('.')[0])
    else:
        total_page_number = int(str(page_number).split('.')[0]) + 1

    #pagination code
    first_prev_page = 0
    second_prev_page = 0
    current_page = 0
    first_next_page = 0
    second_next_page = 0


    if int(request.args['page']) == 1:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = 0
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == 2:
        current_page = int(request.args['page'])
        first_prev_page = 0
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    elif int(request.args['page']) == total_page_number - 1:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = 0
    elif int(request.args['page']) == total_page_number:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = 0
        second_next_page = 0
    elif int(request.args['page']) > 3:
        current_page = int(request.args['page'])
        first_prev_page = current_page - 2
        second_prev_page = current_page - 1
        first_next_page = current_page + 1
        second_next_page = current_page + 2
    else:
        first_prev_page = 1
        second_prev_page = 2
        current_page = 3
        first_next_page = 4
        second_next_page = 5
    #pagination code ends here



    manga_chapter_list_from_paginated_manga = []
    for item in all_manga:
        manga_chapter_list_from_paginated_manga.append(mongo.db.manga_chapter_list.find_one({'manga_id':item['id']}))


    #popular manga view
    front_page_manga = list(mongo.db.update_spider.find())
    popular_manga_list = []

    for item in front_page_manga[0]['popular_manga']:
        # popular_manga_list.append(list(mongo.db.all_manga_details.find_one({'id':item})))
        popular_manga_list.append(mongo.db.all_manga_details.find_one({'id':item}))



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

    return render_template('manga-ongoing.html', all_manga=all_manga, total_manga = total_manga, total_page_number = total_page_number, current_page = current_page, first_prev_page = first_prev_page, second_prev_page = second_prev_page, first_next_page = first_next_page, second_next_page = second_next_page, popular_manga_list=popular_manga_list, genres=genres, categories=categories, total_bookmark=total_bookmark, manga_chapter_list_from_paginated_manga=manga_chapter_list_from_paginated_manga)








# Register route
@app.route('/register/', methods=['POST', 'GET'])
def register():
    if session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        users = mongo.db.users
        current_user = users.find_one({'name' : request.form['username']})

        if current_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass, 'displayname' : request.form['displayname'], 'email' : request.form['email']})
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        error_message = 'Username already exist, please choose different one!'
        return render_template('register.html', error_message = error_message)
    return render_template('register.html')







# Login route
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})

        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            # if  bcrypt.check_password_hash(login_user['password'], request.form['password']):
                session['username'] = request.form['username']
                return redirect(url_for('home'))
            error_message = 'Invalid username or password, Please try again!'
            return render_template('login.html', error_message = error_message)

    return render_template('login.html')






# Logout route
@app.route('/logout/')
def logout():
    if session:
        session.clear()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))






# robots.txt route
@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])





if __name__ == '__main__':
    app.run(debug=True)
