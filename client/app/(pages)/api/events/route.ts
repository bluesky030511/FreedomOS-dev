import { ContactPageSharp } from '@mui/icons-material';
import amqplib from 'amqplib';
import cors from 'cors'; // You might not need this in this context, but it's included for potential use.
import http, { IncomingMessage, ServerResponse } from 'http';

const server = http.createServer();

const accessRabbitMQ = async (
  exchange: string,
  queue: string,
  callback: (message: any) => void
): Promise<void> => {
  const url = 'amqp://guest:guest@localhost:5672/';
  const conn = await amqplib.connect(url);
  const channel = await conn.createChannel();
  
  await channel.assertExchange(exchange, 'fanout', { durable: false });
  const q = await channel.assertQueue(queue);
  await channel.bindQueue(q.queue, exchange, '');

  channel.consume(q.queue, msg => {
    if (msg !== null) {
      const messageContent = JSON.parse(msg.content.toString());
      callback(messageContent);
    }
  }, { noAck: true });
};

server.on('request', (req: IncomingMessage, res: ServerResponse) => {
  if (req.url === '/events') {
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
    res.setHeader('Access-Control-Allow-Credentials', 'true');

    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    const queue = "monitor/robot_state";
    const exchange = 'monitor/robot_state';

    const queueBattery = "monitor/robot_state_low";
    const exchangeBattery = 'monitor/robot_state_low';

    accessRabbitMQ(exchange, queue, (message) => {
      res.write(`event: state\ndata: ${JSON.stringify(message)}\n\n`);
    });

    accessRabbitMQ(exchangeBattery, queueBattery, (message) => {
      res.write(`event: battery\ndata: ${JSON.stringify(message)}\n\n`);
    });
  }
});

server.listen(5000, () => console.log('Server listening on port 5000'));