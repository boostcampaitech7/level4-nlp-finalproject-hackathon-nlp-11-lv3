import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer'
import InputText from '../atom/InputText'

import FileIcon from '../../assets/icon/addFile.png'
import SearchIcon from '../../assets/icon/search.png'
import { requestQuery } from '../../api/query';

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

export default function QueryInput({ height }) {
    const [query, setQuery] = useState();
    const max_tokens = 1000;
    const temperature = 0.7;

    const navigate = useNavigate();

    function onKeyUp(e) {
        if (e.key == 'Enter' && query) {
            onClickSearch();
        }
    }

    function onClickSearch() {
        navigate('/chat', { state : { query }});
        
        // requestQuery(
        //     query,
        //     max_tokens,
        //     temperature,
        //     requestQuerySuccess,
        //     requestQueryFail
        // );
    }

    function requestQuerySuccess(res) {
        console.log(res.data);
    }

    function requestQueryFail(res) {
        console.log(res);
    }

    function onClickFile() {

    }

    return (
        <CustomContainer color='212222' radius='25' width='85' height={height} padding='20'>
            <InputText placeholder='질문을 입력하세요.' autoFocus onKeyUp={onKeyUp} onChange={(e) => setQuery(e.target.value)}/>
            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'flex-end', width: '100%'}}>
                <IconBox onClick={onClickFile}><img src={FileIcon} style={{ width: '26px', height: '100%' }} /></IconBox>
                <IconBox onClick={onClickSearch}><img src={SearchIcon} style={{ width: '26px', height: '100%' }} /></IconBox>
            </Box> 
        </CustomContainer>
    )
}