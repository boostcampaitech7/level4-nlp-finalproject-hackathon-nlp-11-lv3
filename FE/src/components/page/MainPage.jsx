import React, { useEffect, useState } from 'react';

import { styled, Box } from '@mui/system'
import CustomText from '../atom/CustomText';
import SideBar from '../atom/SideBar'

import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import NewsWidget from '../module/NewsWidget';
import QueryInput from '../module/QueryInput';
import SelectModel from '../module/SelectModel';

import LoadingIcon from '../../assets/icon/spinner_black.gif'

export default function MainPage() {
  const [model, setModel] = useState('');
  const [message, setMessage] = useState('');
  const [visibleMessage, setVisibleMessage] = useState('');
  const [visibleIcon, setVisibleIcon] = useState('');

  function handleChange(value) {
    setModel(value);
  };

  function handleUpload(value) {
    setMessage(value);
  }

  useEffect(() => {
    if (message) {
      setVisibleMessage(message);

      if (message === 'PDF 받아라 ~') {
        setVisibleIcon(LoadingIcon);
      } 
      else if (message === '벡터 DB 생성 완료 !') {
        setVisibleIcon('');
        const timer = setTimeout(() => {
          setVisibleMessage('');
        }, 3000);

        return () => clearTimeout(timer);
      }

    }
  }, [message])

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
        <QueryInput height='130' model={model} mode='main' onFileUpload={handleUpload} uploadMessage={message} />
        <SelectModel onModelChange={handleChange} selectedValue={model} />
        <Box sx={{ display: 'flex', height: '40px', margin: '-45px 0 0 0', alignItems: 'center' }}>
          <img src={visibleIcon} style={{ height: '100%' }} />
          <CustomText color='blur' size='xs' height='30px' justifyContent='flex-start'>{visibleMessage}</CustomText>
        </Box>
      </Box>
    </Box>
  );
}
