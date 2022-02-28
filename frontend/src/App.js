import logo from './logo.svg';
import './App.css';

import React from 'react';
import { DataGrid, GridRowsProp, GridColDef } from '@mui/x-data-grid';

const rows: GridRowsProp = [
  { id: 1, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 2, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 3, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 4, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 5, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 6, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 7, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 8, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 9, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 10, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 11, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
  { id: 12, col1: 3000000, col2: 2000000, col3: 4000000, col4: 2000000 },
];

const columns: GridColDef[] = [
  { field: 'col1', headerName: 'CoinCheck Ask', width: 100 },
  { field: 'col2', headerName: 'CoinCheck Bid', width: 100 },
  { field: 'col3', headerName: 'Liquid Ask', width: 100 },
  { field: 'col4', headerName: 'Liquid Bid', width: 100 },
];

export default function App() {
  return (
    <div style={{ height: 1000, width: 700 }}>
      <DataGrid rows={rows} columns={columns} />
    </div>
  );
}
