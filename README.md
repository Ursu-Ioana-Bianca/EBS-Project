# EBS-Project
Evaluation Report: Broker-Based Pub/Sub System
Există trei componente principale: Broker, Publisher și Subscriber.
Brokers sunt noduri care primesc publicații de la Publishers și le distribuie către Subscribers interesați.
Publisher generează publicații aleatorii și le trimit către Brokers.
Subscriber trimit Broker-ilor abonamente pentru a primi anumite publicații și primesc publicațiile care corespund abonamentelor lor.
<br />
În funcțiile specifice:
Broker gestionează conexiuni cu Publishers și Subscribers, precum și distribuția publicațiilor și abonamentelor.
Publisher trimit publicații la Brokers.
Subscriber trimit abonamente la Brokers și primesc publicațiile corespunzătoare.
Există logica pentru salvarea și încărcarea stării pentru Brokers, precum și pentru gestionarea stării în caz de eșec al unui Broker.
<br /><br />
Methodology:
Generate Subscriptions: Create 10,000 simple subscriptions, with two scenarios for comparison:
Scenario 1: Subscriptions containing only equality (=) operators.
Scenario 2: Subscriptions containing equality (=) operators approximately 25% of the time, mixed with other operators (!=, <, <=, >, >=).
Run Publishers: Continuously generate and send publications to the brokers for a 3-minute interval.
Measure Delivery and Latency: Track the number of successfully delivered publications and measure the time from publication emission to reception by subscribers.
Calculate Matching Rate: Compare the number of matched publications in both subscription scenarios.<br />
Results:<br />
Number of Successful Publications Delivered:<br />
- Scenario 1: Subscriptions with equality operators.<br />
Publications sent successfully: 9000<br />
- Scenario 2: Subscriptions with mixed operators.<br />
Publications sent successfully: 9090<br />
Average Delivery Latency:<br /><br />
- Scenario 1: Subscriptions with equality operators.<br />
Average latency: 150 milliseconds<br />
- Scenario 2: Subscriptions with mixed operators.<br />
Average latency: 170 milliseconds
<br />
Matching Rate:
- Scenario 1: 21.4%
- Scenario 2: 94.2%
