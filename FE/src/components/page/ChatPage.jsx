import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom';

import { styled, Box } from '@mui/system'
import SideBar from '../atom/SideBar'

import StockWidget from '../module/StockWidget';
import StockNewsWidget from '../module/StockNewsWidget';
import QueryInput from '../module/QueryInput';
import QueryOutput from '../module/QueryOutput';

import HomeIcon from '../../assets/icon/home.png'; 

import { requestQuery, requestCompany } from '../../api/query';

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

export default function ChatPage() {
    const navigate = useNavigate();
    const location = useLocation(); 
    
    const query = location.state?.query;
    const model = location.state?.model ? location.state.model : 'GPT-4o-mini';
    const [answer, setAnswer] = useState();
    const [company, setCompany] = useState('');

    const max_tokens = 1000;
    const temperature = 0.7;

    function onClickHome() {
        navigate('/');
    }

    function requestApi() {
        requestQuery(
            query,
            model,
            max_tokens,
            temperature,
            requestQuerySuccess,
            requestQueryFail
        ); 
    }
    
    function requestQuerySuccess(res) {
        console.log(res);
        
        setCompany(res.data.company == '네이버' ? 'NAVER' : res.data.company);
        setAnswer(res.data.answer);
    }

    function requestQueryFail(res) {
        console.log('requestQueryFail: ', res);
    }

    useEffect(() => {
        requestApi();
    }, []);

    return (
        <Box sx={{display: 'flex'}}>
        <SideBar>
            <IconBox onClick={onClickHome}><img src={HomeIcon}/></IconBox>
            { company && <StockWidget company={company}/>}
            <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '80%' }}>
                {/* <StockNewsWidget>{company? company : ''}</StockNewsWidget> */}
            </Box>
        </SideBar>
        
        <Box sx={{display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center', width: '100vw', marginBottom: '40px'}}>
            <QueryOutput answer={answer ? answer : ''}>{query}</QueryOutput>
            <QueryInput height='95' />
        </Box>
        </Box>
    );
}
