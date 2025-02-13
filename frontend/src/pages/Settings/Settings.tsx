import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  Divider,
} from '@mui/material';
import {
  Notifications,
  Security,
  Language,
  ColorLens,
  DarkMode,
} from '@mui/icons-material';

export const Settings: React.FC = () => {
  const [settings, setSettings] = React.useState({
    notifications: true,
    darkMode: false,
    twoFactor: false,
    language: 'English',
    theme: 'Light',
  });

  const handleToggle = (setting: keyof typeof settings) => {
    setSettings((prev) => ({
      ...prev,
      [setting]: !prev[setting],
    }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Card>
        <CardContent>
          <List>
            <ListItem>
              <ListItemIcon>
                <Notifications />
              </ListItemIcon>
              <ListItemText
                primary="Notifications"
                secondary="Enable push notifications"
              />
              <Switch
                edge="end"
                checked={settings.notifications}
                onChange={() => handleToggle('notifications')}
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <DarkMode />
              </ListItemIcon>
              <ListItemText
                primary="Dark Mode"
                secondary="Toggle dark/light theme"
              />
              <Switch
                edge="end"
                checked={settings.darkMode}
                onChange={() => handleToggle('darkMode')}
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Security />
              </ListItemIcon>
              <ListItemText
                primary="Two-Factor Authentication"
                secondary="Enable extra security"
              />
              <Switch
                edge="end"
                checked={settings.twoFactor}
                onChange={() => handleToggle('twoFactor')}
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Language />
              </ListItemIcon>
              <ListItemText
                primary="Language"
                secondary={settings.language}
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <ColorLens />
              </ListItemIcon>
              <ListItemText
                primary="Theme"
                secondary={settings.theme}
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
    </Box>
  );
}; 