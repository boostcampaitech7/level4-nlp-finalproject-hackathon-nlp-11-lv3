import React from 'react';
import { useNavigate } from 'react-router-dom';

import Button from '@mui/material/Button';
import CustomText from '../atom/customText';

export default function Home() {
  const navigate = useNavigate();

  function goToChat() {
    navigate('/chat');
  }

  return (
    <div>
      <CustomText size='l' my='20' mx='20'>무엇을 도와드릴까요?</CustomText>
      

      <div>
        <Button onClick={goToChat}>채팅 .. 할래 ..?</Button>
      </div>
    </div>
  );
}
