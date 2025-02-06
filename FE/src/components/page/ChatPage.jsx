import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { Box } from '@mui/system'
import CustomText from '../atom/CustomText';
import SideBar from '../atom/SideBar'

import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import StockNewsWidget from '../module/StockNewsWidget';
import QueryInput from '../module/QueryInput';
import QueryOutput from '../module/QueryOutput';

export default function MainPage() {
  function goToHome() {
    const navigate = useNavigate();
    navigate('/');
  }

  const location = useLocation();
  const query = location.state?.query;
  const companyName = '네이버';

  return (
    <Box sx={{display: 'flex'}}>
      <SideBar>
        <IndexWidget />
        <ExchangeRateWidget />
        <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '80%' }}>
          <StockNewsWidget>{companyName}</StockNewsWidget>
        </Box>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center', width: '100vw', marginBottom: '40px'}}>
        <QueryOutput>{query}</QueryOutput>
        <QueryInput height='95' />
      </Box>
    </Box>
  );
}
