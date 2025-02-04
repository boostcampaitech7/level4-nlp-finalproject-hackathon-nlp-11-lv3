import React from 'react'
import { useNavigate } from 'react-router-dom';

import Button from '@mui/material/Button';
import CustomSpace from '../atom/CustomBox'
import Input from '../atom/Input'

export default function QueryInput() {
    const navigate = useNavigate();
  
    function goToChat() {
      navigate('/chat');
    }

    return (
        <CustomSpace>
            <Input placeholder='질문을 입력하세요.' />
            <Button onClick={goToChat}>검색</Button>
        </CustomSpace>
    )
}