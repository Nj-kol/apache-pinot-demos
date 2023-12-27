import argparse
import logging
import sys
from confluent_kafka import Consumer

logging.basicConfig(
  format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO,
  handlers=[
      logging.StreamHandler(sys.stdout)
  ]
)

logger = logging.getLogger()

def main(args):
    logger.info('Starting consumer')
    conf = {
        'bootstrap.servers': args.bootstrap_server,
        'group.id': 'mygroup',
        'auto.offset.reset': args.offset,
    }

    c = Consumer(conf)
    topic_name = args.topic
    c.subscribe([topic_name])

    logger.info(f'Now reading messages from topic {topic_name}')
    while True:
        msg = c.poll(1.0)
	
        if msg is None:
	        continue 
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue
	
        print('Received message: {}'.format(msg.value().decode('utf-8')))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bootstrap-server')
    parser.add_argument('--topic')
    parser.add_argument('--offset')
    args = parser.parse_args()
    main(args)