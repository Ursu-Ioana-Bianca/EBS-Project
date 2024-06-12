import socket
import threading
import random
import time
import sys



subscription_field_percentages = {
    "company": {"presence": 0.8},
    "value": {"presence": 0.8},
    "drop": {"presence": 0.7},
    "variation": {"presence": 0.6}
}

def generate_subscription(operator_equal):
    subscription = []
    for field, config in subscription_field_percentages.items():
        if random.random() <= config["presence"]:
            if field == "company":
                operator = "="
                value = random.choice(["Google", "Apple", "Microsoft"])
            else:
                operator = "=" if random.random() < operator_equal else random.choice(["!=", "<", "<=", ">", ">="])
                if field == "value":
                    value = random.uniform(80.0, 100.0)
                elif field == "drop":
                    value = random.uniform(5.0, 15.0)
                elif field == "variation":
                    value = random.uniform(0.6, 0.8)
            subscription.append(f"({field},{operator},{value})")

    # Check if subscription is empty
    if not subscription:
        # If empty, generate a default subscription to avoid parsing errors
        field = random.choice(list(subscription_field_percentages.keys()))
        operator = "=" if random.random() < operator_equal else random.choice(["!=", "<", "<=", ">", ">="])
        if field == "company":
            value = random.choice(["Google", "Apple", "Microsoft"])
        elif field == "value":
            value = random.uniform(80.0, 100.0)
        elif field == "drop":
            value = random.uniform(5.0, 15.0)
        elif field == "variation":
            value = random.uniform(0.6, 0.8)
        subscription.append(f"({field},{operator},{value})")

    return "{" + ";".join(subscription) + "}"

class Subscriber:
    def __init__(self, broker_addresses):
        self.broker_addresses = broker_addresses
        self.sockets = []
        self.latencies = []
        self.publication_count = 0
        self.received = []

    def subscribe(self, subscription):
        for address in self.broker_addresses:
            self.send_to_broker(address, subscription)

    def send_to_broker(self, address, subscription):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(address)
            sock.sendall(b"SUBSCRIPTION:" + subscription.encode('utf-8'))
            self.sockets.append(sock)
        except Exception as e:
            print(f"Error connecting to broker {address}: {e}")

    def receive_publication(self, publication):
        if publication not in self.received:
            parts = publication.split(',')
            publication_time = float(parts[-1])  # Extract timestamp from publication
            current_time = time.time()
            latency = current_time - publication_time
            self.latencies.append(latency)
            self.publication_count += 1
            print(f"Received publication: {publication}")
            self.received.append(publication)

    def listen_for_publications(self):
        while True:
            for sock in self.sockets:
                try:
                    self.receive_from_broker(sock)
                except Exception as e:
                    print(f"Error receiving from broker: {e}")
                    self.sockets.remove(sock)
                    sock.close()

    def receive_from_broker(self, sock):
        data = sock.recv(1024).decode('utf-8')
        if data:
            messages = self.parse_messages(data)
            for message_type, content in messages:
                if message_type == "publication":
                    self.receive_publication(content)

    def parse_messages(self, data):
        messages = []
        while data:
            if data.startswith("PUBLICATION:"):
                end_idx = data.find("PUBLICATION:", len("PUBLICATION:"))
                if end_idx == -1:
                    end_idx = len(data)
                message = data[len("PUBLICATION:"):end_idx].strip()
                data = data[end_idx:]
                messages.append(("publication", message))
            else:
                raise ValueError("Invalid message format")
        return messages

def create_subscribers(broker_addresses, num_subscribers):
    subscribers = []
    for _ in range(num_subscribers):
        subscriber = Subscriber(broker_addresses)
        subscription = generate_subscription(0.05)
        print(f"Generated subscription: {subscription}")
        subscriber.subscribe(subscription)
        threading.Thread(target=subscriber.listen_for_publications).start()
        subscribers.append(subscriber)
    return subscribers

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python subscriber.py <broker_port> [<broker_port> ...]")
        sys.exit(1)

    broker_addresses = [("localhost", int(port)) for port in sys.argv[1:]]
    num_subscribers = 3
    subscribers = create_subscribers(broker_addresses, num_subscribers)


    start_time = time.time()
    duration = 185  # seconds
    while time.time() - start_time < duration:
        time.sleep(1)

    # Collect and print statistics after the test duration
    total_publications_received = sum(subscriber.publication_count for subscriber in subscribers)
    all_latencies = [latency for subscriber in subscribers for latency in subscriber.latencies]
    avg_latency = sum(all_latencies) / len(all_latencies) if all_latencies else 0

    print(f"Total publications received: {total_publications_received}")

    print(f"Average publication latency: {avg_latency} seconds")
