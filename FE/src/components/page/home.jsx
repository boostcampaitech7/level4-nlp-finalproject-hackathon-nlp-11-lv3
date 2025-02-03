import React from 'react';
import { useNavigate } from 'react-router-dom';

import Button from '@mui/material/Button';

export default function Home() {
  const navigate = useNavigate();

  function goToChat() {
    navigate('/chat');
  }

  return (
    <div>
      <h1>Home</h1>
      <Button onClick={goToChat}>채팅 .. 할래 ..?</Button>
    </div>
  );
}
