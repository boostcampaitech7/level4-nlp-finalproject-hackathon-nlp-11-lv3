import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import Button from '@mui/material/Button';
import { styled, Box } from '@mui/system'

import CustomText from '../atom/CustomText';
import QueryOutput from '../module/QueryOutput';

import SideBar from '../atom/SideBar'
import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import NewsWidget from '../module/NewsWidget';

export default function MainPage() {
  function goToHome() {
    const navigate = useNavigate();
    navigate('/');
  }

  const location = useLocation();
  const query = location.state?.query;

  return (
    <Box sx={{display: 'flex'}}>
      <SideBar>
        <IndexWidget />
        <ExchangeRateWidget />
        <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '85%' }}>
          <NewsWidget />
        </Box>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'flex-top', alignItems: 'center', width: '100vw'}}>
        <QueryOutput>{query}</QueryOutput>
      </Box>
    </Box>
  );
}
