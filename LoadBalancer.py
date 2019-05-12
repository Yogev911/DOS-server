import multiprocessing

from flask_cors import CORS
from flask import Flask, request, redirect

app = Flask(__name__)
CORS(app)
CPUS = multiprocessing.cpu_count()


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/", methods=['GET'])
def root():
    client_id = int(request.args.get('clientid'))
    return redirect(f"http://localhost:{str((client_id % CPUS) + 8081)}/connection?clientid={client_id}", code=302)


@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...', 200


def worker(port):
    app.run(host="0.0.0.0", port=port)
