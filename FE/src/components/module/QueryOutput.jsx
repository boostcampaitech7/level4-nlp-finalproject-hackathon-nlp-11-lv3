import React, { useState, useEffect } from 'react';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer';
import CustomText from '../atom/CustomText';

import CopyIcon from '../../assets/icon/copy.png'
import ReloadIcon from '../../assets/icon/reload.png'

const IconBox = styled(Box) (
    () => `
    width: 30px;
    display: flex;
    alignItems: center;
    margin: 0px 5px 20px 5px;
    cursor: pointer;
    &:hover {
        opacity: 0.8;
    }
    `
)

export default function QueryOutput({ children, answer }) {    
    const [displayedText, setDisplayedText] = useState('');
    
    function onClickCopy() {
        navigator.clipboard.writeText(answer);
    }

    function onClickReload() {
        window.location.reload();
    }

    useEffect(() => {
        let index = 0;
        
        const interval = setInterval(() => {
            if (index < answer?.length) {
                const char = answer[index];
                
                setDisplayedText((prev) => prev + char);
                index++;
            } else {
                clearInterval(interval);
            }
        }, 20);

        return () => clearInterval(interval);
    }, [answer]);

    return (
        <CustomContainer color='191A1A' radius='25' width='85%' height='auto' flexDirection='column' justifyContent='flex-start' padding='20' my='20px'>
            <CustomText color='blur' weight='bold' size='m' justifyContent='flex-start' my='40' mx='25'>
                {children}
            </CustomText>
            
            <CustomText size='s' weight='bold' justifyContent='flex-start' mx='5'>
                💡 답변
            </CustomText>
            
            <CustomText size='xs' justifyContent='flex-start' textAlign='start' my='20' mx='25'>
                {displayedText}
            </CustomText>
            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', width: '100%'}}>
                <IconBox onClick={onClickCopy}><img src={CopyIcon} style={{ width: '26px', height: '100%' }} /></IconBox>
                <IconBox onClick={onClickReload}><img src={ReloadIcon} style={{ width: '30px', height: '100%' }} /></IconBox>
            </Box> 
        </CustomContainer>
    );
}
