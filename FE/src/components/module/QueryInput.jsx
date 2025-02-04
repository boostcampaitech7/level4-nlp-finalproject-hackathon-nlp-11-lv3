import React from 'react'
import { useNavigate } from 'react-router-dom';
import { styled, Box } from '@mui/system'

import CustomContainer from '../atom/CustomContainer'
import InputText from '../atom/InputText'

import FileIcon from '../../assets/icon/addFile.png'
import SearchIcon from '../../assets/icon/search.png'

const IconBox = styled(Box) (
    () => `
    width: 30px;
    display: flex;
    alignItems: center;
    margin: 20px 5px;
    cursor: pointer;
    &:hover {
        opacity: 0.8;
    }
    `
)

export default function QueryInput() {
    const navigate = useNavigate();
  
    function goToChat() {
      navigate('/chat');
    }

    return (
        <CustomContainer color='212222' radius='25' width='85' height='140'>
            <InputText placeholder='질문을 입력하세요.' autoFocus />
            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'center', width: '100px'}}>
                <IconBox onClick={goToChat}><img src={FileIcon} style={{ width: '100%', height: '100%' }} /></IconBox>
                <IconBox onClick={goToChat}><img src={SearchIcon} style={{ width: '100%', height: '100%' }} /></IconBox>
            </Box> 
        </CustomContainer>
    )
}