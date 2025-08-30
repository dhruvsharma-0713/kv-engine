import gevent
import time
from gevent.server import StreamServer
from gevent import monkey

monkey.patch_all()  # Patches standard libraries for non-blocking I/O

class KeyValueServer:
    def __init__(self):
        self.data_store = {}
        self.aof_file = open("server.aof", "ab")
        self.expiry_times = {}
        self.commands = {
            'SET': self.handle_set,
            'GET': self.handle_get,
            'DELETE': self.handle_delete,
            'FLUSH': self.handle_flush,
            'MGET': self.handle_mget,
            'MSET': self.handle_mset,
            'INCR': self.handle_incr,
            'DBSIZE': self.handle_dbsize,
            'KEYS': self.handle_keys
        }

    def handle_client(self, socket, address):
        print(f"New connection from {address}")
        file_obj = socket.makefile('rwb')  # Binary mode for reading and writing

        while True:
            try:
                line = file_obj.readline()
                if not line:
                    break

                # Decode the incoming command and split into parts
                command, *args = line.strip().split()
                command = command.decode('utf-8').upper()
                write_commands = {'SET', 'DELETE', 'FLUSH', 'MSET'}
                if command in write_commands:
                    self.aof_file.write(line)
                    self.aof_file.flush()

                handler = self.commands.get(command)
                if handler:
                    handler(file_obj, *args)
                else:
                    file_obj.write(b"-ERR unknown command\r\n")

                file_obj.flush()
            except Exception as e:
                file_obj.write(b"-ERROR: " + str(e).encode('utf-8') + b"\r\n")
                file_obj.flush()
                break

        print(f"Connection closed from {address}")

    def handle_set(self, file_obj, key, value, *args):
        key_str = key.decode('utf-8')
        value_str = value.decode('utf-8')
        self.data_store[key_str] = value_str

        # Check for and handle the EX expiry option
        if args and len(args) == 2 and args[0].decode('utf-8').upper() == 'EX':
            try:
                seconds = int(args[1].decode('utf-8'))
                expiry_time = time.time() + seconds
                self.expiry_times[key_str] = expiry_time
            except ValueError:
                pass
        
        file_obj.write(b"+OK\r\n")  

    def handle_delete(self, file_obj, key):
        key = key.decode('utf-8')
        if key in self.data_store:
            del self.data_store[key]
            file_obj.write(b":1\r\n")
        else:
            file_obj.write(b":0\r\n")

    def handle_flush(self, file_obj):
        self.data_store.clear()
        file_obj.write(b"+OK\r\n")  

    def handle_get(self, file_obj, key):
        key_str = key.decode('utf-8')

        if key_str in self.expiry_times:
            if time.time() > self.expiry_times[key_str]:
                # If the key has expired, delete it from both dictionaries
                del self.data_store[key_str]
                del self.expiry_times[key_str]
                
                # Send a "not found" response and exit the function
                file_obj.write(b"$-1\r\n")
                return
        value = self.data_store.get(key_str)
        if value is not None:
            response = f"${len(value)}\r\n{value}\r\n"
            file_obj.write(response.encode('utf-8'))
        else:
            file_obj.write(b"$-1\r\n")

    def handle_mget(self, file_obj, *keys):
        values = []
        for key in keys:
            key_str = key.decode('utf-8')
            values.append(self.data_store.get(key_str))

        response_parts = [f"*{len(values)}\r\n"]
        for value in values:
            if value is None:
                response_parts.append("$-1\r\n")
            else:
                response_parts.append(f"${len(value)}\r\n{value}\r\n")
    
        file_obj.write("".join(response_parts).encode('utf-8'))

    def handle_mset(self, file_obj, *kv_pairs):
        for i in range(0, len(kv_pairs), 2):
            key = kv_pairs[i].decode('utf-8')
            value = kv_pairs[i + 1].decode('utf-8')
            self.data_store[key] = value
        file_obj.write(b"+OK\r\n")

    def start_server(self, host='127.0.0.1', port=1234):
        server = StreamServer((host, port), self.handle_client)
        print(f"Server started on {host}:{port}")
        server.serve_forever()

    def handle_incr(self, file_obj, key):
        key = key.decode('utf-8')
        current_value = self.data_store.get(key, '0')
        try:
            new_value = int(current_value) + 1
            new_value_str = str(new_value)
            self.data_store[key] = new_value_str

            response = f":{new_value_str}\r\n"
            file_obj.write(response.encode('utf-8'))

        except ValueError:
            file_obj.write(b"-ERROR: Value is not an integer or out of range\r\n")
            return
    
    def handle_dbsize(self, file_obj):
        db_size = len(self.data_store)
        response = f":{db_size}\r\n"
        file_obj.write(response.encode('utf-8'))

    def handle_keys(self, file_obj):
        keys = list(self.data_store.keys())
        response_parts = [f"*{len(keys)}\r\n"]
        for key in keys:
            response_parts.append(f"${len(key)}\r\n{key}\r\n")
        
        file_obj.write("".join(response_parts).encode('utf-8'))
        

if __name__ == "__main__":
    kv_server = KeyValueServer()
    kv_server.start_server()
