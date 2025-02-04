import React from 'react';
import { useNavigate } from 'react-router-dom';

import Button from '@mui/material/Button';

export default function ChatPage() {
  const navigate = useNavigate();

  function goToHome() {
    navigate('/');
  }

  return (
    <div>
      <h1>Chat Page</h1>
      <Button onClick={goToHome}>집에 갈래 ..</Button>
    </div>
  );
}
