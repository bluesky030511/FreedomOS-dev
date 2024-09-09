import { useEffect, useState } from 'react';

interface RabbitMQData {
  // Define the structure of your RabbitMQ message data here
  // For example:
  // id: string;
  // status: string;
  // You can modify this interface based on your actual data structure
  [key: string]: any; // This allows for any additional properties
}

const useRabbitMQ = () => {
  const [data, setData] = useState<RabbitMQData | null>(null);
  const [batteryState, setBattery] = useState<RabbitMQData | null>(null);

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:5000/events');

    eventSource.addEventListener('state', (event: MessageEvent) => {
      const messageContent: RabbitMQData = JSON.parse(event.data);
      console.log('Received state:', messageContent); // Debugging log
      setData(messageContent);
    });
    
    eventSource.addEventListener('battery', (event: MessageEvent) => {
      const messageContent: RabbitMQData = JSON.parse(event.data);
      console.log('Received battery:', messageContent); // Debugging log
      setBattery(messageContent);
    });

    eventSource.onerror = (err: Event) => {
      console.error('EventSource failed:', err); // Debugging log
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return { data, batteryState };
};

export default useRabbitMQ;