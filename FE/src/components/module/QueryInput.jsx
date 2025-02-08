import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer'
import InputText from '../atom/InputText'

import FileIcon from '../../assets/icon/addFile.png'
import SearchIcon from '../../assets/icon/search.png'

import { uploadFile } from '../../api/query';

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

export default function QueryInput({ height, model }) {
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const [file, setFile] = useState();
    const [query, setQuery] = useState('');

    function onKeyUp(e) {
        if (e.key == 'Enter' && query) {
            onClickSearch();
        }
    }

    function onClickSearch() {
        if (query) {
            navigate('/chat', { state: { query, model } });
        }
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
        if (file) {
        console.log(file);
        
            const formData = new FormData();
            formData.append('file', file);

            uploadFile(
                formData,
                uploadFileSuccess,
                uploadFileFail
            );
        }
    }, [file])

    return (
        <CustomContainer color='212222' radius='25' width='80%' height={height} padding='20'>
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