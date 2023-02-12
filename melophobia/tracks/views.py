from flask import Blueprint, render_template

from melophobia.db import get_db

tracks_bp = Blueprint('tracks', __name__, template_folder='../templates/tracks')


@tracks_bp.route('/tracks')
def list_tracks():
    mongo = get_db()

    tracks = list(mongo.db.tracks.aggregate([
        {
            '$lookup': {
                'from': "artists",
                'let': {'recorded_artists': '$recorded_artists'},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$recorded_artists"]}}},
                    {'$sort': {"name": 1}}
                ],
                'as': "recorded_artists"
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

    return render_template('tracks_list.html', tracks=tracks)
