import amqp, { Channel, Connection } from 'amqplib';

const AMQP_URL = process.env.AMQP_CONNECTION_STRING || 'amqp://localhost';

let connection: Connection | null = null;
let channel: Channel | null = null;

const initAMQP = async (): Promise<{ connection: Connection; channel: Channel }> => {
  if (connection && channel) {
    return { connection, channel };
  }

  connection = await amqp.connect(AMQP_URL);
  channel = await connection.createChannel();

  return { connection, channel };
};

process.on('exit', async () => {
  if (channel) {
    await channel.close();
  }
  if (connection) {
    await connection.close();
  }
});

export { initAMQP };
