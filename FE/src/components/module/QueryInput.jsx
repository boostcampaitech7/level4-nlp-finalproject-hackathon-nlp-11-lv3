import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer'
import InputText from '../atom/InputText'

import FileIcon from '../../assets/icon/addFile.png'
import SearchIcon from '../../assets/icon/search.png'
import { requestQuery, uploadFile } from '../../api/query';

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
    const [query, setQuery] = useState('');
    const [answer, setAnswer] = useState();
    const [company, setCompany] = useState();
    const [file, setFile] = useState();
    
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const max_tokens = 1000;
    const temperature = 0.7;

    function onKeyUp(e) {
        if (e.key == 'Enter' && query) {
            onClickSearch();
        }
    }

    function onClickSearch() {
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            uploadFile(
                formData,
                uploadFileSuccess,
                uploadFileFail
            );
        }

        requestQuery(
            query,
            max_tokens,
            temperature,
            requestQuerySuccess,
            requestQueryFail
        ); 
    }

    function requestQuerySuccess(res) {
        setAnswer(res.data.answer);
        if (res.data.company == '네이버') setCompany('NAVER');
        else setCompany(res.data.company);
    }

    function requestQueryFail(res) {
        console.log(res);
    }

    function onClickFile() {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    }

    function handleFileChange(e) {
        setFile(e.target.files[0]);
    }

    function uploadFileSuccess(res) {
        console.log('file upload success: ', res);             
    }

    function uploadFileFail(res) {
        console.log('file upload fail');        
    }

    useEffect(() => {
        if (answer && company) {
            navigate('/chat', { state: { query, answer, company } });
        }        
    }, [answer, company, file]);
    

    return (
        <CustomContainer color='212222' radius='25' width='85' height={height} padding='20'>
            <InputText placeholder='질문을 입력하세요.' autoFocus onKeyUp={onKeyUp} onChange={(e) => setQuery(e.target.value)}/>
            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-end', justifyContent: 'flex-end', width: '100%'}}>
                <IconBox onClick={onClickFile}>
                    <div className='flex flex-col gap-2.5' >
                        <label htmlFor='file-upload'>
                            <img src={FileIcon} style={{ width: '26px', height: '100%', cursor:'pointer' }} />
                        </label>
                        <input type='file' id='file-upload' accept='.pdf' className='hidden' onChange={handleFileChange} />
                    </div>
                </IconBox>
                <IconBox onClick={onClickSearch}><img src={SearchIcon} style={{ width: '26px', height: '100%' }} /></IconBox>
            </Box> 
        </CustomContainer>
    )
}