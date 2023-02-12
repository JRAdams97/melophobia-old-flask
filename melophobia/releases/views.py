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
        }, {
            '$sort': {"title": 1}
        }
    ]))

    return render_template('releases_list.html', releases=releases)
