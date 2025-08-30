from flask import Flask, render_template_string
from kv_client import KeyValueClient

app = Flask(__name__)

# A simple HTML template for our dashboard
HTML_TEMPLATE = """
<!doctype html>
<html>
    <head>
        <title>KV Store Dashboard</title>
        <style>
            body { font-family: sans-serif; background: #282c34; color: #abb2bf; margin: 2em; }
            h1 { color: #61afef; text-align: center;}
            .container { display: flex; justify-content: space-around; align-items: flex-start; }
            .metric { background: #3b4048; padding: 2em; border-radius: 8px; text-align: center; margin-bottom: 2em;}
            .metric-value { font-size: 3em; font-weight: bold; color: #98c379; }
            .error { color: #e06c75; }
            table { border-collapse: collapse; width: 400px; background: #3b4048; }
            th, td { border: 1px solid #282c34; padding: 8px; text-align: left; }
            th { background-color: #61afef; color: #282c34; }
        </style>
    </head>
    <body>
        <h1>Key-Value Store Dashboard</h1>
        <div class="container">
            <div class="metric">
                <h2>Keys in Database</h2>
                {% if error %}
                    <p class="error">{{ error }}</p>
                {% else %}
                    <p class="metric-value">{{ db_size }}</p>
                {% endif %}
            </div>
            <div>
                <h2>All Keys & Values</h2>
                {% if not error and kv_data %}
                <table>
                    <tr>
                        <th>Key</th>
                        <th>Value</th>
                    </tr>
                    {% for key, value in kv_data.items() %}
                    <tr>
                        <td>{{ key }}</td>
                        <td>{{ value }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% elif not error %}
                <p>No keys found.</p>
                {% endif %}
            </div>
        </div>
    </body>
</html>
"""

@app.route("/")
def dashboard():
    client = KeyValueClient()
    try:
        client.connect()
        # Fetch stats
        db_size = client.dbsize()
        keys = client.keys()
        
        kv_data = {}
        if keys:
            # The mget response is complex, we need to parse it
            raw_values_response = client.mget(*keys)
            lines = raw_values_response.strip().split('\r\n')
            values = lines[2::2]
            kv_data = dict(zip(keys, values))

        return render_template_string(HTML_TEMPLATE, db_size=db_size, kv_data=kv_data, error=None)
    except ConnectionRefusedError:
        error_msg = "Could not connect to the KV server. Is it running?"
        return render_template_string(HTML_TEMPLATE, error=error_msg)
    finally:
        client.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)