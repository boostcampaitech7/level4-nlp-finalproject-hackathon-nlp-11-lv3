import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Main() {
  const navigate = useNavigate();

  function goToChat() {
    navigate('/chat');
  }

  return (
    <div>
      <h1>Main Page</h1>
      <button onClick={goToChat}>채팅 .. 할래 ..?</button>
    </div>
  );
}
