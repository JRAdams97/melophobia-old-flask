import pymongo
from bson import ObjectId
from flask import Blueprint, render_template, request

from melophobia.db import get_db
from melophobia.enum import Country

artists_bp = Blueprint('artists', __name__, template_folder='../templates/artists')


@artists_bp.route('/artists')
def artists_list():
    mongo = get_db()

    artists = list(mongo.db.artists.aggregate([
        {
            '$lookup': {
                'from': "genres",
                'let': {'genres': "$genres"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "genres"
            }
        }, {
            '$sort': {"name": 1}
        }
    ]))

    return render_template('artists_list.html', artists=artists)


@artists_bp.route('/artist/<_id>')
def artist_detail(_id):
    mongo = get_db()

    artist = list(mongo.db.artists.aggregate([
        {
            '$match': {'_id': ObjectId(_id)}
        }, {
            '$lookup': {
                'from': "genres",
                'let': {'genres': "$genres"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "genres"
            }
        }, {
            '$lookup': {
                'from': "releases",
                'let': {'releases': "$releases"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$releases"]}}},
                    {'$sort': {"release_date": -1}}
                ],
                'as': "releases"
            }
        }, {
            '$sort': {"name": 1}
        }
    ]))

    return render_template('artist_detail.html', artist=artist[0])


@artists_bp.route('/artist', methods=['GET', 'POST'])
def artist_create():
    mongo = get_db()

    all_genres = list(mongo.db.genres.find().sort("name"))

    if request.method == "GET":
        return render_template('artist_form.html', all_genres=all_genres, countries=[e.value for e in Country])

    if request.method == "POST":
        genres = [ObjectId(genre) for genre in request.form.getlist('genres')]
        favourite = 'favourite' in request.form

        formation_country = None

        if request.form['formation_country'] != '':
            formation_country_enum = Country(request.form['formation_country'])
            formation_country = {'country_name': formation_country_enum.value,
                                 'country_code': formation_country_enum.code,
                                 'wikidata_id': formation_country_enum.wikidata}

        disband_country = None

        if request.form['disband_country'] != '':
            disband_country_enum = Country(request.form['disband_country'])
            disband_country = {'country_name': disband_country_enum.value, 'country_code': disband_country_enum.code,
                               'wikidata_id': disband_country_enum.wikidata}

        ipis = request.form['ipis'].split('\r\n')

        data = {'name': request.form['name'], 'genres': genres, 'formation_date': request.form['formation_date'],
                'formation_area': request.form['formation_area'], 'formation_country': formation_country,
                'disband_date': request.form['disband_date'], 'disband_area': request.form['disband_area'],
                'disband_country': disband_country, 'favourite': favourite, 'artist_type': request.form['artist_type'],
                'releases': [], 'ipis': ipis, 'isni': request.form['isni'], 'wikidata_id': request.form['wikidata_id']}

        mongo.db.artists.insert_one(data)

        print("Successfully created new artist [name : {}, country : {}]".format(
            request.form['name'], formation_country.formation_country_name))

        return artists_list()


@artists_bp.route('/artist/edit/<_id>', methods=['GET', 'POST'])
def artist_update(_id):
    mongo = get_db()

    artist = list(mongo.db.artists.aggregate([
        {
            '$match': {'_id': ObjectId(_id)}
        }, {
            '$lookup': {
                'from': "genres",
                'let': {'genres': "$genres"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "genres"
            }
        }, {
            '$lookup': {
                'from': "releases",
                'let': {'releases': "$releases"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$releases"]}}},
                    {'$sort': {"release_date": -1}}
                ],
                'as': "releases"
            }
        }, {
            '$sort': {"name": 1}
        }
    ]))

    all_genres = list(mongo.db.genres
                      .find({'_id': {'$nin': [ObjectId(_id)]}})
                      .sort("name", pymongo.ASCENDING))

    if request.method == "GET":
        countries = [e.value for e in Country]
        selected_genres = []

        for genre_val in artist[0]['genres']:
            selected_genres.append(genre_val['_id'])

        ipi_str = '\r\n'.join(artist[0]['ipis'])

        return render_template('artist_form.html', artist=artist[0], selected_genres=selected_genres,
                               all_genres=all_genres, countries=countries, ipis=ipi_str)

    if request.method == "POST":
        genres = [ObjectId(genre) for genre in request.form.getlist('genres')]
        favourite = 'favourite' in request.form

        formation_country = None

        if request.form['formation_country'] != '':
            formation_country_enum = Country(request.form['formation_country'])
            formation_country = {'country_name': formation_country_enum.value,
                                 'country_code': formation_country_enum.code,
                                 'wikidata_id': formation_country_enum.wikidata}

        disband_country = None

        if request.form['disband_country'] != '':
            disband_country_enum = Country(request.form['disband_country'])
            disband_country = {'country_name': disband_country_enum.value, 'country_code': disband_country_enum.code,
                               'wikidata_id': disband_country_enum.wikidata}

        ipis = request.form['ipis'].split('\r\n')

        data = {'name': request.form['name'], 'formation_date': request.form['formation_date'],
                'formation_area': request.form['formation_area'], 'formation_country': formation_country,
                'disband_date': request.form['disband_date'], 'disband_area': request.form['disband_area'],
                'disband_country': disband_country, 'favourite': favourite, 'artist_type': request.form['artist_type'],
                'ipis': ipis, 'isni': request.form['isni'], 'wikidata_id': request.form['wikidata_id']}

        mongo.db.artists.update_one({'_id': ObjectId(_id)}, {'$set': {'genres': []}})
        mongo.db.artists.update_one({'_id': ObjectId(_id)}, {'$addToSet': {"genres": {'$each': genres}}})
        mongo.db.artists.update_one({'_id': ObjectId(_id)}, {'$set': data})

        print("Successfully modified artist [id : {}]".format(_id))

        return artists_list()
