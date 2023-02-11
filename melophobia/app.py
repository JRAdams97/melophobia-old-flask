from flask import Flask, render_template


def create_app():
    _app = Flask(__name__, instance_relative_config=True, static_url_path='', static_folder='static',
                 template_folder='templates')
    _app.config["MONGO_URI"] = 'mongodb+srv://admin:T6PsBgmpzdmQNAxX@melophobia-serverless.4jsys.mongodb.net' \
                               '/melophobia?retryWrites=true&w=majority'

    from .artists.views import artists_bp
    from .genres.views import genres_bp

    _app.register_blueprint(artists_bp)
    _app.register_blueprint(genres_bp)

    @_app.route('/')
    def index():
        return render_template("index.html")

    return _app


if __name__ == '__main__':
    app = create_app()
    app.run()
