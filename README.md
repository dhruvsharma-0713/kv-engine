# KV-Engine: A Python-Based Key-Value Store

KV-Engine is a high-performance, in-memory key-value database server built with Python and Gevent, inspired by Redis. It features data persistence, key expiry, a comprehensive test suite, and a real-time web dashboard for monitoring.



---

## Features

* **Networked Server:** Built with `gevent`, the server handles multiple client connections concurrently and efficiently.
* **Data Persistence (AOF):** Utilizes an Append-Only File (`server.aof`) to log all write operations, ensuring data durability across server restarts.
* **Key Expiry (TTL):** Supports `SET key value EX seconds` for automatic key deletion, making it ideal for caching and session management.
* **Rich Command Set:** Implements a variety of commands, including:
    * `SET`, `GET`, `DELETE`, `FLUSH`
    * `MSET`, `MGET` for batch operations.
    * `INCR` for atomic integer manipulation.
    * `DBSIZE`, `KEYS` for database introspection.
* **Test-Driven Development (TDD):** A robust test suite with `pytest` covers all server commands and features, ensuring code reliability and correctness.
* **Web Dashboard:** A real-time monitoring dashboard built with `Flask` that connects to the server to display the total number of keys and a live table of all key-value pairs.

---

## How to Run

### 1. Prerequisites
* Python 3.x
* Git

### 2. Setup & Installation
Clone the repository and set up a virtual environment.
```bash
Clone the repository

Create and activate a virtual environment
python -m venv venv
# On Windows:
# .\\venv\\Scripts\\activate
# On macOS/Linux:
# source venv/bin/activate
```
Install the required dependencies manually:
```bash
pip install gevent
pip install pytest
pip install Flask
```

### 3. Running the Application
You will need three separate terminals to run the full application.

* **Terminal 1: Start the Server**
    ```bash
    python kv_server.py
    ```
* **Terminal 2: (Optional) Add Sample Data**
    Run the client script to populate the database with some initial data.
    ```bash
    python kv_client.py
    ```
* **Terminal 3: Start the Web Dashboard**
    ```bash
    python dashboard.py
    ```
### 4. View the Dashboard
Open your web browser and navigate to **`http://127.0.0.1:5000`** to see the live dashboard.
