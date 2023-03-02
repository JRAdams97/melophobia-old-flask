import pymongo
from bson import ObjectId
from flask import Blueprint, render_template, request

from melophobia.db import get_db

genres_bp = Blueprint('genres', __name__, template_folder='../templates/genres')


@genres_bp.route('/genres')
def genres_list():
    mongo = get_db()

    genres = list(mongo.db.genres.aggregate([
        {
            '$lookup': {
                'from': "genres",
                'let': {'parent_genres': '$parent_genres'},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$parent_genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "parent_genres"
            }
        }, {
            '$sort': {"name": 1}
        }
    ]))

    return render_template('genres_list.html', genres=genres)


@genres_bp.route('/genre', methods=['GET', 'POST'])
def genre_create():
    mongo = get_db()

    all_genres = list(mongo.db.genres.find().sort("name"))

    if request.method == "GET":
        return render_template('genre_form.html', all_genres=all_genres)

    if request.method == "POST":
        parent_genres = [ObjectId(genre) for genre in request.form.getlist('parent_genres')]
        favourite = 'favourite' in request.form

        data = {'name': request.form['name'], 'origin_year': request.form['origin_year'],
                'parent_genres': parent_genres, 'favourite': favourite, 'wikidata_id': request.form['wikidata_id']}

        mongo.db.genres.insert_one(data)

        return genres_list()


@genres_bp.route('/genre/<_id>', methods=['GET', 'POST'])
def genre_update(_id):
    mongo = get_db()

    genre = list(mongo.db.genres.aggregate([
        {
            '$match': {'_id': ObjectId(_id)}
        }, {
            '$lookup': {
                'from': "genres",
                'let': {'parent_genres': '$parent_genres'},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$parent_genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "parent_genres"
            }
        }
    ]))

    all_genres = list(mongo.db.genres
                      .find({'_id': {'$nin': [ObjectId(_id)]}})
                      .sort("name", pymongo.ASCENDING))

    if request.method == "GET":
        selected_genres = []

        for genre_val in genre[0]['parent_genres']:
            selected_genres.append(genre_val['_id'])

        return render_template('genre_form.html', genre=genre[0], selected_genres=selected_genres,
                               all_genres=all_genres)

    if request.method == "POST":
        parent_genres = [ObjectId(genre) for genre in request.form.getlist('parent_genres')]
        favourite = 'favourite' in request.form

        data = {'name': request.form['name'], 'origin_year': request.form['origin_year'], 'favourite': favourite,
                'wikidata_id': request.form['wikidata_id']}

        print(data)

        mongo.db.genres.update_one({'_id': ObjectId(_id)}, {'$set': {'parent_genres': []}})
        mongo.db.genres.update_one({'_id': ObjectId(_id)}, {'$addToSet': {"parent_genres": {'$each': parent_genres}}})
        mongo.db.genres.update_one({'_id': ObjectId(_id)}, {'$set': data})

        return genres_list()
