import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

const mockOffers = [
  {
    id: 1,
    type: 'Points Multiplier',
    value: '2x',
    conditions: 'Min. spend $50',
    startDate: '2024-02-01',
    endDate: '2024-02-29',
    status: 'Active',
    redemptions: 234,
  },
  {
    id: 2,
    type: 'Points Bonus',
    value: '500 points',
    conditions: 'Min. spend $75',
    startDate: '2024-02-15',
    endDate: '2024-03-15',
    status: 'Scheduled',
    redemptions: 0,
  },
  // Add more mock data as needed
];

export const Offers: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [newOffer, setNewOffer] = useState({
    type: '',
    value: '',
    conditions: '',
    startDate: '',
    endDate: '',
  });

  const handleCreateOffer = () => {
    // Handle offer creation logic here
    setOpenDialog(false);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Offers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Offer
        </Button>
      </Box>

      <Grid container spacing={3}>
        {mockOffers.map((offer) => (
          <Grid item xs={12} md={6} key={offer.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">{offer.type}</Typography>
                  <Chip
                    label={offer.status}
                    color={offer.status === 'Active' ? 'success' : 'default'}
                  />
                </Box>
                <Typography variant="h5" gutterBottom>
                  {offer.value}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {offer.conditions}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Valid: {offer.startDate} to {offer.endDate}
                  </Typography>
                  <Typography variant="body2">
                    Redemptions: {offer.redemptions}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Offer Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Offer</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Offer Type</InputLabel>
              <Select
                value={newOffer.type}
                onChange={(e) => setNewOffer({ ...newOffer, type: e.target.value })}
                label="Offer Type"
              >
                <MenuItem value="Points Multiplier">Points Multiplier</MenuItem>
                <MenuItem value="Points Bonus">Points Bonus</MenuItem>
                <MenuItem value="Cross Banner">Cross Banner</MenuItem>
                <MenuItem value="Category Discount">Category Discount</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Value"
              value={newOffer.value}
              onChange={(e) => setNewOffer({ ...newOffer, value: e.target.value })}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Conditions"
              value={newOffer.conditions}
              onChange={(e) => setNewOffer({ ...newOffer, conditions: e.target.value })}
              sx={{ mb: 2 }}
            />

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  value={newOffer.startDate}
                  onChange={(e) => setNewOffer({ ...newOffer, startDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="End Date"
                  type="date"
                  value={newOffer.endDate}
                  onChange={(e) => setNewOffer({ ...newOffer, endDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateOffer}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 