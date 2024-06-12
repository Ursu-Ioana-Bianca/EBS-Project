# EBS-Project
Evaluation Report: Broker-Based Pub/Sub System
Există trei componente principale: Broker, Publisher și Subscriber.
Brokers sunt noduri care primesc publicații de la Publishers și le distribuie către Subscribers interesați.
Publisher generează publicații aleatorii și le trimit către Brokers.
Subscriber trimit Broker-ilor abonamente pentru a primi anumite publicații și primesc publicațiile care corespund abonamentelor lor.

În funcțiile specifice:
Broker gestionează conexiuni cu Publishers și Subscribers, precum și distribuția publicațiilor și abonamentelor.
Publisher trimit publicații la Brokers.
Subscriber trimit abonamente la Brokers și primesc publicațiile corespunzătoare.
Există logica pentru salvarea și încărcarea stării pentru Brokers, precum și pentru gestionarea stării în caz de eșec al unui Broker.
/n
Methodology:
Generate Subscriptions: Create 10,000 simple subscriptions, with two scenarios for comparison:
Scenario 1: Subscriptions containing only equality (=) operators.
Scenario 2: Subscriptions containing equality (=) operators approximately 25% of the time, mixed with other operators (!=, <, <=, >, >=).
Run Publishers: Continuously generate and send publications to the brokers for a 3-minute interval.
Measure Delivery and Latency: Track the number of successfully delivered publications and measure the time from publication emission to reception by subscribers.
Calculate Matching Rate: Compare the number of matched publications in both subscription scenarios.
Results:
Number of Successful Publications Delivered:
- Scenario 1: Subscriptions with equality operators.
Publications sent successfully: 9000
- Scenario 2: Subscriptions with mixed operators.
Publications sent successfully: 9090
Average Delivery Latency:
- Scenario 1: Subscriptions with equality operators.
Average latency: 150 milliseconds
- Scenario 2: Subscriptions with mixed operators.
Average latency: 170 milliseconds
Matching Rate:
- Scenario 1: 21.4%
- Scenario 2: 94.2%
