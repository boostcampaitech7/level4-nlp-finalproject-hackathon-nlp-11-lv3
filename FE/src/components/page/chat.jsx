import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Chat() {
  const navigate = useNavigate();

  function goToMain() {
    navigate('/');
  }

  return (
    <div>
      <h1>Chat Page</h1>
      <button onClick={goToMain}>집에 갈래 ..</button>
    </div>
  );
}
