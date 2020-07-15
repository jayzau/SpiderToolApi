from app import create_app
from config.settings import APP_CONFIG

app = create_app()


if __name__ == '__main__':
    app.run(**APP_CONFIG)
