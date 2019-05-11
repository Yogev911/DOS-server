import multiprocessing
from flask_cors import CORS
from flask import Flask, request, redirect

app = Flask(__name__)
CORS(app)

TIME_FRAME = 5
MAX_CONNECTIONS = 5
CPUS = multiprocessing.cpu_count()


@app.route("/", methods=['GET'])
def root():
    client_id = int(request.args.get('clientid'))
    return redirect(f"http://localhost:{str((client_id % CPUS) + 8081)}/connection?clientid={client_id}", code=302)


def worker(port):
    app.run(host="0.0.0.0", port=port)
