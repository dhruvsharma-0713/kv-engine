import socket

class KeyValueClient:
    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def send_command(self, command):
        if self.sock is None:
            raise ConnectionError("Not connected to the server.")
        
        self.sock.sendall(command.encode('utf-8') + b'\r\n')
        return self.receive_response()

    def receive_response(self):
        response = self.sock.recv(4096).decode('utf-8')
        return response

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Connection closed.")

    def set(self, key, value):
        return self.send_command(f"SET {key} {value}")

    def get(self, key):
        return self.send_command(f"GET {key}")

    def delete(self, key):
        return self.send_command(f"DELETE {key}")

    def flush(self):
        return self.send_command(f"FLUSH")

    def mget(self, *keys):
        return self.send_command(f"MGET {' '.join(keys)}")

    def mset(self, *kv_pairs):
        return self.send_command(f"MSET {' '.join(kv_pairs)}")
    
    def dbsize(self):
        response = self.send_command("DBSIZE")
        return response.strip().replace(":", "")
    
    def keys(self):
        response = self.send_command("KEYS")
        # We need to parse it to get a list of keys
        lines = response.strip().split('\r\n')
        if not lines or not lines[0].startswith('*'):
            return []
        
        return lines[2::2]

if __name__ == "__main__":
    client = KeyValueClient()
    client.connect()

    try:
        # Example usage of the client
        print(client.set("name", "Dhruv"))
        print(client.get("name"))
        print(client.set("age", "22"))
        print(client.mget("name", "age"))
        print(client.delete("name"))
        print(client.get("name"))
        #print(client.flush())
    finally:
        client.close()
