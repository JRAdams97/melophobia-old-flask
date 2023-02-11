from flask import Blueprint, render_template

from melophobia.db import get_db

genres_bp = Blueprint('genres', __name__, template_folder='../templates/genres')


@genres_bp.route('/genres')
def list_genres():
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
