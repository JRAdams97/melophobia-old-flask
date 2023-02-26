from bson import ObjectId
from flask import Blueprint, render_template

from melophobia.db import get_db

releases_bp = Blueprint('releases', __name__, template_folder='../templates/releases')


@releases_bp.route('/releases')
def list_releases():
    mongo = get_db()

    releases = list(mongo.db.releases.aggregate([
        {
            '$lookup': {
                'from': "artists",
                'let': {'artists': '$artists'},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$artists"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "artists"
            }
        }, {
            '$lookup': {
                'from': "genres",
                'let': {'genres': '$genres'},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$genres"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "genres"
            }
        }
    ]))

    releases = sorted(releases, key=lambda rd: (rd['release_date'].split('/')[2],
                                                rd['release_date'].split('/')[1],
                                                rd['release_date'].split('/')[0]), reverse=True)

    return render_template('releases_list.html', releases=releases)


@releases_bp.route('/releases/<_id>')
def release_detail(_id):
    mongo = get_db()

    release = list(mongo.db.releases.aggregate([
        {
            '$match': {'_id': ObjectId(_id)}
        }, {
            '$lookup': {
                'from': "artists",
                'let': {'artists': "$artists"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$artists"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "artists"
            }
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
        }
    ]))

    return render_template('release_detail.html', release=release[0])
