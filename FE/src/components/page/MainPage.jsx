import React from 'react';
import { styled, Box, margin, bgcolor } from '@mui/system'

import CustomText from '../atom/CustomText';
import QueryInput from '../module/QueryInput';

import SideBar from '../atom/SideBar'
import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import NewsWidget from '../module/NewsWidget';

export default function MainPage() {
  return (
    <Box sx={{display: 'flex'}}>
      <SideBar>
        <IndexWidget />
        <ExchangeRateWidget />
        <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '85%' }}>
          <NewsWidget />
        </Box>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', width: '100vw'}}>
        <CustomText weight='bold' size='l' my='20' mx='20'>주식을 검색해 드릴까요?</CustomText>
        <QueryInput />
      </Box>
    </Box>
  );
}
