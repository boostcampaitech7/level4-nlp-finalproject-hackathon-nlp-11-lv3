import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { styled, Box } from '@mui/system';
import SideBar from '../atom/SideBar';
import IconBox from '../atom/IconBox';

import StockWidget from '../module/StockWidget';
import QueryInput from '../module/QueryInput';
import QueryOutput from '../module/QueryOutput';

import HomeIcon from '../../assets/icon/home.png';

import { requestQuery } from '../../api/query';

export default function ChatPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const hasFetched = useRef(false);

  const query = location.state?.query;
  const model = location.state?.model || 'GPT-4o-mini';

  const [sessionId, setSessionId] = useState('');
  const [queries, setQueries] = useState([query]);
  const [answers, setAnswers] = useState([]);
  const [company, setCompany] = useState(location.state?.company);
  const [chatHistory, setChatHistory] = useState([]);  
  

  const max_tokens = 1000;
  const temperature = 0.7;

  function onClickHome() {
    navigate('/');
  }

  function handleQuerySubmit(newQuery) {
    setQueries((prev) => [...prev, newQuery]);
    requestApi(newQuery);
  }

  function handleCompanySubmit(newCompany) {    
    setCompany(newCompany);
  }

  function requestApi(query) {
    requestQuery(
        sessionId,
        query,
        company === 'NAVER' ? '네이버' : company,
        model,
        max_tokens,
        temperature,
        chatHistory,
        (res) => {     
            console.log(res);
            setSessionId(res.data.session_id);
            if (company === '') setCompany(res.data.company === '네이버' ? 'NAVER' : res.data.company);
            setAnswers((prev) => [...prev, res.data.answer]);
            setChatHistory(res.data.chat_history);
        },
        (err) => console.log('requestQueryFail:', err)
    );
  }

  useEffect(() => {
    if (!hasFetched.current && query) {
      hasFetched.current = true;
      requestApi(query);
    }
  }, [query]);

  return (
    <Box sx={{ display: 'flex' }}>
      <SideBar>
        <IconBox onClick={onClickHome}><img src={HomeIcon} /></IconBox>
        {company && <StockWidget company={company} />}
        <Box sx={{ marginTop: 'auto', marginBottom: '20px', width: '80%' }}>
            {/* <StockNewsWidget>{company? company : ''}</StockNewsWidget> */}
        </Box>
      </SideBar>

      <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', alignItems: 'center', width: '100vw', margin: '60px 0 40px 0' }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', alignItems: 'center', width: '90%', height: '600px', overflowY: 'auto' }}>
          {queries.map((q, idx) => (
            <QueryOutput key={idx} answer={answers[idx] || ''}>{q}</QueryOutput>
          ))}
        </Box>
        <QueryInput sessionId={sessionId} height='95' onQuerySubmit={handleQuerySubmit} onCompanySubmit={handleCompanySubmit} />
      </Box>
    </Box>
  );
}