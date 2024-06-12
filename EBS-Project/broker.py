import socket
import sys
import threading
import time
import json
import os
from collections import defaultdict


class Broker:
    def __init__(self, broker_id, address, next_broker_addresses=None):
        self.broker_id = broker_id
        self.address = address
        self.next_broker_addresses = next_broker_addresses or []
        self.routing_table = defaultdict(list)
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind_socket()
        self.publication_queue = []
        self.sent_publications = defaultdict(set)
        self.data_file = "broker_data.json"
        self.load_state_from_file()
        threading.Thread(target=self.listen_for_connections).start()
        threading.Thread(target=self.process_publications).start()
        threading.Thread(target=self.send_heartbeat).start()

    def bind_socket(self):
        port_increment = 0
        max_attempts = 10
        while port_increment < max_attempts:
            try:
                self.server_socket.bind(self.address)
                self.server_socket.listen(5)
                return
            except OSError as e:
                if e.errno == 10048:
                    self.address = (self.address[0], self.address[1] + 1)
                    port_increment += 1
                else:
                    raise
        sys.exit(1)

    def send_heartbeat(self):
        while True:
            for next_broker_address in self.next_broker_addresses:
                try:
                    next_broker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    next_broker_socket.connect(next_broker_address)
                    heartbeat_message = f"HEARTBEAT:{self.broker_id}".encode('utf-8')
                    next_broker_socket.sendall(heartbeat_message)
                except Exception as e:
                    # Handle failure by attempting to take over state
                    self.take_over_state(next_broker_address)
                finally:
                    next_broker_socket.close()
            time.sleep(5) 

    def take_over_state(self, failed_broker_address):
        # Attempt to take over state from the failed broker
        for next_broker_address in self.next_broker_addresses:
            if next_broker_address != failed_broker_address:
                try:
                    next_broker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    next_broker_socket.connect(next_broker_address)
                    next_broker_socket.sendall(b"REQUEST_STATE")
                    response = next_broker_socket.recv(4096)
                    if response.startswith(b"STATE_DATA:"):
                        state_data = response[len("STATE_DATA:"):]
                        self.load_state_from_data(state_data)
                        print(f"Took over state from {next_broker_address}")
                        break
                except Exception as e:
                    print(f"Error taking over state from {next_broker_address}: {e}")
                finally:
                    next_broker_socket.close()

    def save_state_to_file(self):
        data = {
            "routing_table": dict(self.routing_table),
            "publication_queue": self.publication_queue
        }
        with open(self.data_file, "w") as file:
            json.dump(data, file)

    def load_state_from_data(self, state_data):
        try:
            data = json.loads(state_data.decode('utf-8'))
            self.routing_table = defaultdict(list, data.get("routing_table", {}))
            self.publication_queue = data.get("publication_queue", [])
            self.sent_publications = defaultdict(set)
            print("State loaded successfully")
        except Exception as e:
            print(f"Error loading state: {e}")



    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024)
            if data:
                message_type, content = self.parse_message(data)
                if message_type == "subscription":
                    self.add_subscription(content.decode('utf-8'), client_socket)
                elif message_type == "publication":
                    publication = content.decode('utf-8')
                    self.route_publication(publication)
                elif message_type == "REQUEST_STATE":
                    self.send_state(client_socket)
        except Exception as e:
            None

    def send_state(self, client_socket):
        state_data = {
            "routing_table": dict(self.routing_table),
            "publication_queue": self.publication_queue
        }
        serialized_state = json.dumps(state_data).encode('utf-8')
        client_socket.sendall(b"STATE_DATA:" + serialized_state)

    def listen_for_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()



    def parse_message(self, data):
        if data.startswith(b"SUBSCRIPTION:"):
            return "subscription", data[len("SUBSCRIPTION:"):]
        elif data.startswith(b"PUBLICATION:"):
            return "publication", data[len("PUBLICATION:"):]
        else:
            raise ValueError("Invalid message format")

    def process_publications(self):
        while True:
            if self.publication_queue:
                publication = self.publication_queue.pop(0)
                self.route_publication(publication)
                self.save_state_to_file()  # Save state after processing each publication
            time.sleep(0.1)

    def route_publication(self, publication):
        self.publication_queue.append(publication)
        matching_subscribers = set()
        with self.lock:
            for subscription, subscribers in self.routing_table.items():
                if self.match(subscription, publication):
                    matching_subscribers.update(subscribers)

        for subscriber_socket in matching_subscribers:
            self.send_publication_to_subscriber(subscriber_socket, publication)

        self.send_publication_to_next_available_broker(publication)

    def match(self, subscription, publication):
        subscription_fields = self.parse_subscription(subscription)
        publication_fields = self.parse_publication(publication)

        for field, operator, value in subscription_fields:
            pub_value = publication_fields.get(field)
            if pub_value is None:
                return False
            if not self.evaluate_condition(pub_value, operator, value):
                return False
        return True

    def parse_subscription(self, subscription):
        conditions = []
        subscription = subscription.strip('{}')
        for condition in subscription.split(';'):
            field, operator, value = condition.strip('()').split(',')
            conditions.append((field, operator, self.parse_value(field, value)))
        return conditions

    def parse_publication(self, publication):
        try:
            fields = publication.split(',')
            return {
                "company": fields[0],
                "value": float(fields[1]),
                "drop": float(fields[2]),
                "variation": float(fields[3]),
                "date": fields[4],
                "timestamp": float(fields[5])
            }
        except ValueError as e:
            print(f"Error parsing publication: {publication} -> {e}")
            return {}

    def parse_value(self, field, value):
        if field in {"value", "drop", "variation"}:
            return float(value)
        return value

    def evaluate_condition(self, pub_value, operator, sub_value):
        if operator == "=":
            return pub_value == sub_value
        elif operator == "!=":
            return pub_value != sub_value
        elif operator == "<":
            return pub_value < sub_value
        elif operator == "<=":
            return pub_value <= sub_value
        elif operator == ">":
            return pub_value > sub_value
        elif operator == ">=":
            return pub_value >= sub_value
        return False

    def send_publication_to_subscriber(self, subscriber_socket, publication):
        try:
            serialized_publication = publication.encode('utf-8')
            if publication not in self.sent_publications[subscriber_socket]:
                subscriber_socket.sendall(b"PUBLICATION:" + serialized_publication)
                self.sent_publications[subscriber_socket].add(publication)
        except Exception as e:
            subscriber_socket.close()

    def send_publication_to_next_available_broker(self, publication):
        for next_broker_address in self.next_broker_addresses:
            success = self.send_publication_to_next_broker(publication, next_broker_address)
            if success:
                break

    def send_publication_to_next_broker(self, publication, next_broker_address, retries=3, delay=1):
        attempt = 0
        while attempt < retries:
            try:
                next_broker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                next_broker_socket.connect(next_broker_address)
                serialized_publication = publication.encode('utf-8')
                next_broker_socket.sendall(b"PUBLICATION:" + serialized_publication)
                next_broker_socket.close()
                return True
            except ConnectionRefusedError as e:
                print(f"ConnectionRefusedError: {e}. Attempt {attempt + 1}/{retries}")
                attempt += 1
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            except Exception as e:
                print(f"Error sending publication to next broker: {e}")
                break  # For other exceptions, break the loop
        return False

    def add_subscription(self, subscription, client_socket):
        with self.lock:
            self.routing_table[subscription].append(client_socket)
            self.save_state_to_file()  # Save state after adding subscription
        self.forward_subscription_to_next_available_broker(subscription)

    def forward_subscription_to_next_available_broker(self, subscription):
        for next_broker_address in self.next_broker_addresses:
            success = self.forward_subscription(subscription, next_broker_address)
            if success:
                break

    def forward_subscription(self, subscription, next_broker_address, retries=3, delay=1):
        attempt = 0
        while attempt < retries:
            try:
                next_broker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                next_broker_socket.connect(next_broker_address)
                next_broker_socket.sendall(b"SUBSCRIPTION:" + subscription.encode('utf-8'))
                next_broker_socket.close()
                return True
            except ConnectionRefusedError as e:
                print(f"ConnectionRefusedError: {e}. Attempt {attempt + 1}/{retries}")
                attempt += 1
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            except Exception as e:
                print(f"Error forwarding subscription to next broker: {e}")
                break  # For other exceptions, break the loop
        return False



if __name__ == "__main__":
    broker_id = int(sys.argv[1])
    address = ("localhost", int(sys.argv[2]))
    next_broker_addresses = [("localhost", int(port)) for port in sys.argv[3:]]
    broker = Broker(broker_id, address, next_broker_addresses)
    print(f"Broker {broker_id} running at {broker.address}")
