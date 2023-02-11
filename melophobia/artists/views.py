from flask import Blueprint, render_template

from melophobia.db import get_db

artists_bp = Blueprint('artists', __name__, template_folder='../templates/artists')


@artists_bp.route('/artists')
def list_artists():
    mongo = get_db()

    artists = list(mongo.db.artists.aggregate([
        {
            '$lookup': {
                'from': "genres",
                'let': {'genres': "$genres"}, 'pipeline': [
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
