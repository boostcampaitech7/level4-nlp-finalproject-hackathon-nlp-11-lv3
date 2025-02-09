import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer'
import IconBox from '../atom/IconBox';
import InputText from '../atom/InputText'

import FileIcon from '../../assets/icon/addFile.png'
import SearchIcon from '../../assets/icon/search.png'

import { uploadFile } from '../../api/query';

export default function QueryInput({ height, model, mode, onQuerySubmit, onCompanySubmit, onFileUpload, uploadMessage }) {
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const [file, setFile] = useState();
    const [query, setQuery] = useState('');

    // Company Mapping

    const dictionary = [
        { keywords: ['네이버', 'naver', 'NAVER'], mappedValue: 'NAVER' },
        { keywords: ['롯데렌탈', '롯데 렌탈'], mappedValue: '롯데렌탈' },
        { keywords: ['엘앤에프'], mappedValue: '엘앤에프' },
        { keywords: ['카뱅', '카카오 뱅크', '카카오뱅크'], mappedValue: '카카오뱅크' },
        { keywords: ['크래프톤'], mappedValue: '크래프톤' },
        { keywords: ['한화솔루션', '한화 솔루션'], mappedValue: '한화솔루션' },
        { keywords: ['제일제당', 'CJ제일제당', 'CJ 제일제당', 'cj제일제당', 'cj 제일제당'], mappedValue: 'CJ제일제당' },
        { keywords: ['LG화학', 'LG 화학', 'lg화학', 'lg 화학', '엘지화학', '엘지 화학'], mappedValue: 'LG화학' },
        { keywords: ['SK케미칼', 'SK 케미칼', 'sk케미칼', 'sk 케미칼', '케미칼'], mappedValue: 'SK케미칼' },
        { keywords: ['SK하이닉스', 'SK 하이닉스', 'sk하이닉스', 'sk 하이닉스', '하이닉스'], mappedValue: 'SK하이닉스' },
    ]

    function mapCompany(input) {
        for (const mapping of dictionary) {
            if (mapping.keywords.some((keyword) => input.includes(keyword))) {
                return mapping.mappedValue;               
            }
        }
        return '';
    }

    // Query Input

    function onKeyUp(e) {
        if (e.key == 'Enter' && query.trim()) {
            onClickSearch();
        }
    }

    function onClickSearch() {     
        if (query.trim()) {
            const company = mapCompany(query);
            if (onCompanySubmit) onCompanySubmit(company); 

            if (mode === 'main') {                
                navigate('/chat', { state: { query, model, company } });
            }
            else if (onQuerySubmit) {
                onCompanySubmit(company);
                onQuerySubmit(query);
                setQuery('');                
            }
        }
    }

    // File Upload

    function onClickFile() {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    }

    function handleFileChange(e) {
        setFile(e.target.files[0]);
        // onFileUpload('PDF 받아라 ~');        
    }

    function uploadFileSuccess(res) {      
        onFileUpload('PDF 전송 완료 !');
    }

    function uploadFileFail(res) {
        onFileUpload('실패 !');
    }    

    useEffect(() => {
        if (file) {        
            const formData = new FormData();
            formData.append('file', file);

            uploadFile(formData, uploadFileSuccess, uploadFileFail);
        }
    }, [file])

    return (
        <CustomContainer color='212222' radius='25' width='80%' height={height} padding='20'>
            <InputText placeholder='질문을 입력하세요.' autoFocus onKeyUp={onKeyUp} onChange={(e) => setQuery(e.target.value)} value={query}/>
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