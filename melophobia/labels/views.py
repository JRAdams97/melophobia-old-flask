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
