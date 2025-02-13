import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';

const mockCustomers = [
  {
    id: 1,
    customerId: 'CUST001',
    name: 'John Doe',
    segment: 'High Value',
    totalPoints: 5432,
    lastActivity: '2024-02-12',
    preferredBanner: 'Sobeys',
  },
  {
    id: 2,
    customerId: 'CUST002',
    name: 'Jane Smith',
    segment: 'Frequent Shopper',
    totalPoints: 3245,
    lastActivity: '2024-02-11',
    preferredBanner: 'Safeway',
  },
  // Add more mock data as needed
];

const columns: GridColDef[] = [
  {
    field: 'customerId',
    headerName: 'Customer ID',
    width: 130,
  },
  {
    field: 'name',
    headerName: 'Name',
    width: 150,
  },
  {
    field: 'segment',
    headerName: 'Segment',
    width: 150,
  },
  {
    field: 'totalPoints',
    headerName: 'Total Points',
    width: 130,
    valueFormatter: (params) => params.value.toLocaleString(),
  },
  {
    field: 'lastActivity',
    headerName: 'Last Activity',
    width: 130,
  },
  {
    field: 'preferredBanner',
    headerName: 'Preferred Banner',
    width: 150,
  },
];

export const Customers: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [paginationModel, setPaginationModel] = useState({
    pageSize: 10,
    page: 0,
  });

  const filteredCustomers = mockCustomers.filter((customer) =>
    Object.values(customer).some(
      (value) =>
        value &&
        value.toString().toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customers
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search customers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box sx={{ height: 600 }}>
            <DataGrid
              rows={filteredCustomers}
              columns={columns}
              paginationModel={paginationModel}
              onPaginationModelChange={setPaginationModel}
              pageSizeOptions={[10, 25, 50]}
              checkboxSelection
              disableRowSelectionOnClick
              density="comfortable"
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}; 