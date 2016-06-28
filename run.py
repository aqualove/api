import os

from api.app import app


if __name__ == '__main__':
    # On Bluemix, get the port number from the environment variable VCAP_APP_PORT
    # When running this app on the local machine, default the port to 8080
    port = int(os.getenv('VCAP_APP_PORT', 8080))
    app.run(port=port)
