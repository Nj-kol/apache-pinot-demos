import argparse
import logging
import sys
from confluent_kafka import Producer

def main(args):
    print('Starting Producer')
    brokers = args.broker_list
    topic = args.topic
    interactive = args.interactive
    file_path = args.file_path

    conf = {
		'bootstrap.servers': f'{brokers}',
		'linger.ms': 200,
		'partitioner': 'murmur2_random',
		'security.protocol' : 'PLAINTEXT',
		'broker.version.fallback' : '0.9.0.1',
		'api.version.request' : 'false'
	}
    
    p = Producer(conf)
    def delivery_report(err, msg):
	    """ Called once for each message produced to indicate delivery result.
	        Triggered by poll() or flush(). """
	    if err is not None:
	        print('Message delivery failed: {}'.format(err))
	    else:
	        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    if interactive:
        print("Interactive mode")
        while True:
            user_input = input("Enter something (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Exiting the program.")
                break
            p.produce(topic, user_input.encode('utf-8'), callback=delivery_report)
            p.flush()

    else:
        print(f"file path is {file_path}")
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    # Remove the newline character at the end of each line
                    line = line.rstrip()
                    p.produce(topic, line.encode('utf-8'), callback=delivery_report)
                    p.flush()
        except FileNotFoundError:
            print(f"The file at path '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker-list')
    parser.add_argument('--topic')
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode")
    parser.add_argument('--file-path')
    args = parser.parse_args()
    main(args)