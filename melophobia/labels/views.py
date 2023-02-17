from bson import ObjectId
from flask import Blueprint, render_template

from melophobia.db import get_db

labels_bp = Blueprint('labels', __name__, template_folder='../templates/labels')


@labels_bp.route('/labels')
def list_labels():
    mongo = get_db()

    labels = list(mongo.db.labels.aggregate([
        {
            '$project': {
                'name': 1,
                'formation_country.country_name': 1,
                'formation_date': 1,
                'closing_date': 1,
                'label_code': 1,
                'catalogue_total': {'$cond': {
                    'if': {'$isArray': "$catalogue_items"},
                    'then': {'$size': "$catalogue_items"},
                    'else': 0
                }},
                'favourite': 1
            }
        }
    ]))

    return render_template('labels_list.html', labels=labels)


@labels_bp.route('/labels/<_id>')
def label_detail(_id):
    mongo = get_db()

    label = list(mongo.db.labels.aggregate([
        {
            '$match': {'_id': ObjectId(_id)}
        }, {
            '$lookup': {
                'from': "catalogue_items",
                'let': {'catalogue_items': "$catalogue_items"},
                'pipeline': [
                    {'$match': {'$expr': {'$in': ["$_id", "$$catalogue_items"]}}},
                    {'$sort': {"catalogue_id": 1}}
                ],
                'as': "catalogue_items"
            }
        }, {
            '$unwind': "$catalogue_items"
        }, {
            '$lookup': {
                'from': "releases",
                'localField': "catalogue_items.release",
                'foreignField': "_id",
                'as': "catalogue_items.release"
            }
        }, {
            '$unwind': {
                "path": "$catalogue_items.release",
                "preserveNullAndEmptyArrays": True
            }
        }, {
            '$lookup': {
                'from': "artists",
                'localField': "catalogue_items.release.artists",
                'foreignField': "_id",
                'as': "catalogue_items.release.artists"
            }
        }, {
            '$group': {
                '_id': "$_id",
                'catalogue_items': {'$push': "$catalogue_items"},
                'first': {'$first': "$$ROOT"}
            }
        }, {
            '$replaceRoot': {
                'newRoot': {
                    '$mergeObjects': ['$first', {'catalogue_items': "$catalogue_items"}]
                }
            }
        }, {
            '$sort': {"name": 1}
        }
    ]))

    print(label)

    return render_template('label_detail.html', label=label[0])
