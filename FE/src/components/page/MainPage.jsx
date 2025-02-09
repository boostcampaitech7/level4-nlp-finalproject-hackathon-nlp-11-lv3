import React, { useEffect, useState } from 'react';

import { styled, Box } from '@mui/system'
import CustomText from '../atom/CustomText';
import SideBar from '../atom/SideBar'
import IconBox from '../atom/IconBox';

import IndexWidget from '../module/IndexWidget';
import ExchangeRateWidget from '../module/ExchangeRateWidget';
import NewsWidget from '../module/NewsWidget';
import QueryInput from '../module/QueryInput';
import SelectModel from '../module/SelectModel';

import LoadingIcon from '../../assets/icon/spinner_black.gif'
import Logo from '../../assets/logo.png'

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
      else if (message === 'PDF 전송 완료 !') {
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
      <Box sx={{ position: 'absolute', width: '60px', margin: '30px 0 0 85px' }}><img src={Logo} /></Box>
      <SideBar>
        <IndexWidget />
        <ExchangeRateWidget />
        <Box sx={{ marginTop: 'auto', marginBottom: '20px' }}>
          <NewsWidget />
        </Box>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', width: '100vw'}}>
        <CustomText weight='bold' size='xl' my='15' mx='20'>{'원하는 금융정보를 검색해보세요 ' + '🔎'}</CustomText>
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
