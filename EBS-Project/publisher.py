import random
import socket
import sys
import time


class Publisher:
    def __init__(self, broker_addresses):
        self.broker_addresses = broker_addresses
        self.nr = 0

    def publish(self, publication):
        for address in self.broker_addresses:
            self.send_to_broker(address, publication)

    def send_to_broker(self, address, publication):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.nr += 1
            sock.connect(address)
            serialized_publication = self.serialize_publication(publication)
            sock.sendall(b"PUBLICATION:" + serialized_publication)

    @staticmethod
    def serialize_publication(publication):
        company = publication['company']
        value = publication['value']
        drop = publication['drop']
        variation = publication['variation']
        date = publication['date']
        timestamp = publication['timestamp']
        return f"{company},{value},{drop},{variation},{date},{timestamp}".encode('utf-8')

def generate_publication():
    company = random.choice(["Google", "Apple", "Microsoft"])
    value = random.uniform(80.0, 100.0)
    drop = random.uniform(5.0, 15.0)
    variation = random.uniform(0.6, 0.8)
    date = f"{random.randint(1, 28)}.{random.randint(1, 12)}.{random.randint(2020, 2023)}"
    timestamp = time.time()  # Include current time as a timestamp
    return {'company': company, 'value': value, 'drop': drop, 'variation': variation, 'date': date, 'timestamp': timestamp}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python publisher.py <broker_port> [<broker_port> ...]")
        sys.exit(1)

    broker_ports = [int(port) for port in sys.argv[1:]]
    broker_addresses = [("localhost", port) for port in broker_ports]

    publisher = Publisher(broker_addresses)
    start_time = time.time()

    while time.time() - start_time < 180:
        publication = generate_publication()
        print(f"Generated publication: {publication}")
        publisher.publish(publication)

        time.sleep(0.1)

    print(f"Number of publications sent: {publisher.nr}")
