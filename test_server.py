import io
import time
import pytest
from kv_server import KeyValueServer

def test_set_and_get():
    server = KeyValueServer()
    # We use BytesIO to simulate a network connection in memory
    mock_socket_file = io.BytesIO()

    # Execute the SET command handler
    key = b'name'
    value = b'Gemini'
    server.handle_set(mock_socket_file, key, value)

    # Execute the GET command handler
    # We need to reset the mock file for the next operation
    mock_socket_file.seek(0) 
    server.handle_get(mock_socket_file, key)

    # Get the value that was "written" to our mock socket
    response = mock_socket_file.getvalue()
    
    # The expected response for GET is "$6\r\nGemini\r\n"
    expected_response = f"${len(value.decode())}\r\n{value.decode()}\r\n".encode('utf-8')

    assert response == expected_response

def test_delete_key():
    server = KeyValueServer()
    # Pre-load the data store with a key to delete
    server.data_store['city'] = 'Bulandshahr'
    mock_socket_file = io.BytesIO()

    # Execute
    key_to_delete = b'city'
    server.handle_delete(mock_socket_file, key_to_delete)

    # Assert that the key is no longer in the data store
    assert key_to_delete.decode() not in server.data_store
    
    # Assert that the correct response (":1\r\n") was sent
    assert mock_socket_file.getvalue() == b':1\r\n'

def test_flush():
    server = KeyValueServer()
    # Pre-load the data store with some data
    server.data_store['key1'] = 'value1'
    server.data_store['key2'] = 'value2'
    mock_socket_file = io.BytesIO()

    # Execute
    server.handle_flush(mock_socket_file)

    # Assert that the data store is now empty
    assert not server.data_store
    
    # Assert that the correct response was sent
    assert mock_socket_file.getvalue() == b'+OK\r\n'

def test_mget():
    server = KeyValueServer()
    # Pre-load the data store with some data
    server.data_store['key1'] = 'value1'
    server.data_store['key2'] = 'value2'
    mock_socket_file = io.BytesIO()

    # Execute
    keys = [b'key1', b'key2']
    server.handle_mget(mock_socket_file, *keys)

    # Assert that the correct response was sent
    assert mock_socket_file.getvalue() == b'*2\r\n$6\r\nvalue1\r\n$6\r\nvalue2\r\n'

def test_mset():
    server = KeyValueServer()
    mock_socket_file = io.BytesIO()

    # Execute
    kv_pairs = [b'key1', b'value1', b'key2', b'value2']
    server.handle_mset(mock_socket_file, *kv_pairs)

    # Assert that the correct response ("+OK\r\n") was sent
    assert mock_socket_file.getvalue() == b'+OK\r\n'

    # Assert that the data store has the expected key-value pairs
    assert server.data_store == {'key1': 'value1', 'key2': 'value2'}

def test_incr_new_key():
    server = KeyValueServer()
    mock_socket_file = io.BytesIO()
    key = b'counter'

    # Execute (This will fail because handle_incr doesn't exist yet)
    server.handle_incr(mock_socket_file, key)

    # Assert that the new value is 1 and the response is correct
    assert server.data_store['counter'] == '1'
    assert mock_socket_file.getvalue() == b':1\r\n'

def test_incr_existing_key():
    server = KeyValueServer()
    # Pre-load an existing value
    server.data_store['counter'] = '5' 
    mock_socket_file = io.BytesIO()
    key = b'counter'

    # Execute
    server.handle_incr(mock_socket_file, key)

    # Assert that the value was incremented correctly to 6
    assert server.data_store['counter'] == '6'
    assert mock_socket_file.getvalue() == b':6\r\n'

def test_incr_with_non_integer_value():
    server = KeyValueServer()
    # Pre-load a non-integer value
    server.data_store['mykey'] = 'hello'
    mock_socket_file = io.BytesIO()
    key = b'mykey'

    # Execute
    server.handle_incr(mock_socket_file, key)

    # Assert that the server sends back an error message
    expected_error = b"-ERROR: Value is not an integer or out of range\r\n"
    assert mock_socket_file.getvalue() == expected_error

def test_set_with_expiry():
    server = KeyValueServer()
    server.expiry_times = {}
    mock_socket_file = io.BytesIO()

    # Execute
    key = b'session'
    value = b'user123'
    expiry_seconds = b'10'

    server.handle_set(mock_socket_file, key, value, b'EX', expiry_seconds)

    # Assert that the key was set in the data_store
    assert server.data_store[key.decode()] == value.decode()

    # Assert that the expiry time was recorded
    expected_expiry_time = time.time() + int(expiry_seconds)
    # We use pytest.approx because time.time() can have tiny floating point variations
    assert server.expiry_times[key.decode()] == pytest.approx(expected_expiry_time, abs=0.1)

def test_get_expired_key():
    server = KeyValueServer()
    mock_socket_file = io.BytesIO()
    key = b'temp'
    value = b'data'
    
    # Set a key with a 1-second expiry
    server.handle_set(mock_socket_file, key, value, b'EX', b'1')
    
    # Wait for a little over 1 second so the key expires
    time.sleep(1.1)
    
    mock_socket_file.seek(0)
    mock_socket_file.truncate(0)
    server.handle_get(mock_socket_file, key)
    
    # Assert that the server returns a "not found" response
    assert mock_socket_file.getvalue() == b'$-1\r\n'

def test_dbsize():
    server = KeyValueServer()
    server.data_store['key1'] = 'value1'
    server.data_store['key2'] = 'value2'
    mock_socket_file = io.BytesIO()

    # Execute
    server.handle_dbsize(mock_socket_file)

    # Assert that the correct response was sent
    assert mock_socket_file.getvalue() == b':2\r\n'

def test_keys():
    server = KeyValueServer()
    server.data_store['name'] = 'Gemini'
    server.data_store['city'] = 'Bulandshahr'
    mock_socket_file = io.BytesIO()

    server.handle_keys(mock_socket_file)

    # Assert
    response = mock_socket_file.getvalue()
    expected_response1 = b'*2\r\n$4\r\nname\r\n$4\r\ncity\r\n'
    expected_response2 = b'*2\r\n$4\r\ncity\r\n$4\r\nname\r\n'
    assert response in (expected_response1, expected_response2)


