from flask import Flask, render_template, send_from_directory


def create_app():
    _app = Flask(__name__, instance_relative_config=True, static_url_path='', static_folder='static',
                 template_folder='templates')
    _app.config["MONGO_URI"] = 'mongodb+srv://admin:xxxx@melophobia-serverless.4jsys.mongodb.net' \
                               '/melophobia?retryWrites=true&w=majority'

    from .artists.views import artists_bp
    from .genres.views import genres_bp
    from .labels.views import labels_bp
    from .releases.views import releases_bp
    from .tracks.views import tracks_bp

    _app.register_blueprint(artists_bp)
    _app.register_blueprint(genres_bp)
    _app.register_blueprint(labels_bp)
    _app.register_blueprint(releases_bp)
    _app.register_blueprint(tracks_bp)

    @_app.route('/')
    def index():
        return render_template("index.html")

    @_app.route('/media/<path:filename>')
    def media_static(filename):
        return send_from_directory(_app.root_path + '/../media/', filename)

    return _app


if __name__ == '__main__':
    app = create_app()
    app.run()
