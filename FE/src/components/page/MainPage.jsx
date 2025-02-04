import React from 'react';
import { styled, Box } from '@mui/system'

import SideBar from '../atom/SideBar'
import CustomText from '../atom/CustomText';
import QueryInput from '../module/QueryInput';

export default function MainPage() {
  return (
    <Box sx={{display: 'flex'}}>
      <SideBar>
      </SideBar>
      
      <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', width: '100vw'}}>
        <CustomText weight='bold' size='l' my='20' mx='20'>무엇을 도와드릴까요?</CustomText>
        <QueryInput />
      </Box>
    </Box>
  );
}
