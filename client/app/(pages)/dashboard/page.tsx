import { Box, Grid, List, ListItem, ListItemText, Paper, Typography } from '@mui/material';
import { styled } from '@mui/system';
import React, { useState } from 'react';
import RobotMap from '../components/RobotMap';
import useRabbitMQ from '../hooks/useRabbitMQ';

// Define the type for the battery state
interface BatteryState {
  battery_soc_percent: number;
}

// Define the type for the data received from RabbitMQ
interface RabbitMQData {
  global_position?: {
    x: number;
    y: number;
  };
  healthy?: boolean;
}

// Custom styled component for the Battery Icon
const BatteryIconContainer = styled('div')<{ battery: number }>(({ theme, battery }) => ({
  position: 'relative',
  width: 24,
  height: 30,
  marginRight: theme.spacing(1),
  border: '1px solid black',
  borderRadius: 4,
  backgroundColor: 'gray',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    width: '100%',
    height: `${battery}%`,
    backgroundColor: 'green',
    borderRadius: 4,
  },
}));

const Home: React.FC = () => {
  const { data, batteryState } = useRabbitMQ();
  console.log('data: ', data);
  console.log('battery: ', batteryState);
  const [activeTask, setActiveTask] = useState<string | null>(null);

  const tasks = ['Task1', 'Task2', 'Task3', 'Task4'];

  const handleClick = (task: string) => {
    setActiveTask(task);
  };

  const position: [number, number] = data?.global_position
    ? [data.global_position.x, data.global_position.y]
    : [51.505, -0.09]; // Default position

  const health = data?.healthy || false;
  const battery = (batteryState?.battery_state as BatteryState)?.battery_soc_percent ?? 20;

  return (
    <Box sx={{ bgcolor: 'white', width: '100%', height: '100vh', display: 'flex' }}>
      <Grid container spacing={4} sx={{ p: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4 }}>
            <Box display="flex" alignItems="center" gap={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Box
                  sx={{
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    bgcolor: health ? 'green' : 'gray',
                    marginRight: 2,
                  }}
                />
                <Typography variant="h6">Healthy</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <BatteryIconContainer battery={battery} />
                <Typography variant="h6">Battery: {battery}%</Typography>
              </Box>
            </Box>
            <RobotMap position={position} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4 }}>
            <Typography variant="h6" align="center" gutterBottom>
              Task List
            </Typography>
            <List>
              {tasks.map((task, index) => (
                <ListItem
                  key={index}
                  button
                  onClick={() => handleClick(task)}
                  selected={activeTask === task}
                  sx={{
                    bgcolor: activeTask === task ? 'primary.main' : 'grey.300',
                    color: activeTask === task ? 'white' : 'black',
                    mb: 1,
                  }}
                >
                  <ListItemText primary={task} />
                  {activeTask === task && (
                    <Typography component="span" sx={{ position: 'absolute', right: 16, fontSize: 14, color: 'white' }}>
                      (active)
                    </Typography>
                  )}
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Home;