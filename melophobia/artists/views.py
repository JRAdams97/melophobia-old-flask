from bson import ObjectId
from flask import Blueprint, render_template

from melophobia.db import get_db

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


@artists_bp.route('/artists/<_id>')
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

    print(artist)

    return render_template('artist_detail.html', artist=artist[0])
