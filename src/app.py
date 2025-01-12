import os
from flask import Flask, send_from_directory
from earn.index import earn
from werkzeug.serving import make_ssl_devcert
from multiprocessing import Process
from utils import current_path
from gevent import pywsgi

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.register_blueprint(earn)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(current_path(), "favicon.ico", mimetype="image/vnd.microsoft.icon")

caTuple = make_ssl_devcert(os.path.join(current_path(), "datas", "secrets", "ca"))
server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, certfile=caTuple[0], keyfile=caTuple[1], do_handshake_on_connect=False)
server.start()

def serveForever():
    server.start_accepting()
    server._stop_event.wait()

if __name__ == "__main__":
    server.serve_forever()
    # for i in range(2):
    #     p = Process(target=serveForever)
    #     p.start()
