import React, { useEffect, useState } from 'react';

import { styled, Box } from '@mui/system'
import CustomText from '../atom/CustomText';
import SideBar from '../atom/SideBar'

import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import NewsWidget from '../module/NewsWidget';
import QueryInput from '../module/QueryInput';
import SelectModel from '../module/SelectModel';

export default function MainPage() {
  const [model, setModel] = useState('');

  function handleChange(value) {
    setModel(value);
  };

  useEffect(() => {
  }, [model])

  return (
    <Box sx={{display: 'flex'}}>
      <SideBar>
        <IndexWidget />
        <ExchangeRateWidget />
        <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '80%' }}>
          <NewsWidget />
        </Box>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', width: '100vw'}}>
        <CustomText weight='bold' size='xl' my='15' mx='20'>주식을 검색해 드릴까요?</CustomText>
        <QueryInput height='130' model={model} mode='main' />
        <SelectModel onModelChange={handleChange} selectedValue={model} />
      </Box>
    </Box>
  );
}
