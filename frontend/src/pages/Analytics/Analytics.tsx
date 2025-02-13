import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface OfferPerformance {
  date: string;
  redemptions: number;
  views: number;
}

interface SegmentDistribution {
  name: string;
  value: number;
}

interface TopOffer {
  id: number;
  type: string;
  redemptions: number;
  conversionRate: string;
  averageValue: string;
}

const mockData = {
  offerPerformance: [
    { date: '2024-02-01', redemptions: 145, views: 567 },
    { date: '2024-02-02', redemptions: 167, views: 623 },
    { date: '2024-02-03', redemptions: 189, views: 589 },
    { date: '2024-02-04', redemptions: 156, views: 645 },
    { date: '2024-02-05', redemptions: 178, views: 678 },
  ] as OfferPerformance[],
  segmentDistribution: [
    { name: 'High Value', value: 234 },
    { name: 'Frequent Shopper', value: 567 },
    { name: 'Occasional', value: 345 },
    { name: 'New Customer', value: 123 },
  ] as SegmentDistribution[],
  topOffers: [
    {
      id: 1,
      type: 'Points Multiplier',
      redemptions: 456,
      conversionRate: '23.4%',
      averageValue: '$67.89',
    },
    {
      id: 2,
      type: 'Points Bonus',
      redemptions: 345,
      conversionRate: '19.8%',
      averageValue: '$54.32',
    },
    {
      id: 3,
      type: 'Cross Banner',
      redemptions: 234,
      conversionRate: '15.6%',
      averageValue: '$78.90',
    },
  ] as TopOffer[],
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export const Analytics: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics
      </Typography>

      <Grid container spacing={3}>
        {/* Offer Performance Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Offer Performance Over Time
              </Typography>
              <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockData.offerPerformance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="redemptions"
                      stroke="#8884d8"
                      name="Redemptions"
                    />
                    <Line
                      type="monotone"
                      dataKey="views"
                      stroke="#82ca9d"
                      name="Views"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Segment Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Customer Segment Distribution
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={mockData.segmentDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: { name: string; percent: number }) =>
                        `${name} (${(percent * 100).toFixed(0)}%)`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {mockData.segmentDistribution.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Performing Offers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Performing Offers
              </Typography>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Offer Type</TableCell>
                      <TableCell align="right">Redemptions</TableCell>
                      <TableCell align="right">Conversion Rate</TableCell>
                      <TableCell align="right">Avg. Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockData.topOffers.map((offer) => (
                      <TableRow key={offer.id}>
                        <TableCell>{offer.type}</TableCell>
                        <TableCell align="right">{offer.redemptions}</TableCell>
                        <TableCell align="right">{offer.conversionRate}</TableCell>
                        <TableCell align="right">{offer.averageValue}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 