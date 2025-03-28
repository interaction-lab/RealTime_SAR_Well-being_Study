from flask import Flask, request, Response
import queue
import threading
from flask_cors import CORS

# this is a wrapper on the Flask server class that contains an queue to keep getting the next information from the Realtime Web App
class FlaskServerWrapper:
    def __init__(self, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.state_queue = queue.Queue(maxsize=2)
        self.current_state = None
        self.host = host
        self.port = port
        self._setup_routes()
        CORS(self.app)

    def _setup_routes(self):
        @self.app.route('/receive_data', methods=['POST'])
        def receive_data():
            data = request.get_json()  # json format
            if not data:
                return 'Invalid data', 400

            self._update_state(data)
            return 'OK', 200

        @self.app.route('/stream')
        def stream():
            def event_stream():
                last_state = None
                while True:
                    if not self.state_queue.empty():
                        new_state = self.state_queue.get()
                        if new_state != last_state:
                            last_state = new_state
                            yield f"data: {new_state}\n\n"
            return Response(event_stream(), content_type='text/event-stream')

    def _update_state(self, new_state):
        if not self.state_queue.empty():
            self.state_queue.get()
        self.state_queue.put(new_state)
        self.current_state = new_state

    def get_state(self):
        return self.current_state

    def run(self):
        threading.Thread(target=self._run_flask, daemon=True).start()

    def _run_flask(self):
        self.app.run(host=self.host, port=self.port, threaded=True)
