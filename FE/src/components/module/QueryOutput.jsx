import React, { useState, useEffect } from 'react';

import { styled, Box } from '@mui/system'
import CustomContainer from '../atom/CustomContainer';
import CustomText from '../atom/CustomText';
import IconBox from '../atom/IconBox';

import CopyIcon from '../../assets/icon/copy.png'
import ReloadIcon from '../../assets/icon/reload.png'
import LoadingIcon from '../../assets/icon/spinner.gif'

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
            <CustomText color='blur' weight='bold' size='m' justifyContent='flex-start' my='40' mx='25' textAlign='start'>
                {children}
            </CustomText>
            
            {displayedText ? 
                <Box sx={{ display: 'flex', height: '50px', margin: '-10px 0 10px 0' }}>
                    <CustomText size='s' weight='bold' justifyContent='flex-start' mx='20'>💬</CustomText>
                    <CustomText size='s' weight='bold' justifyContent='flex-start' mx='-10'>답변</CustomText>
                </Box>
                :
                <Box sx={{ display: 'flex', height: '50px', margin: '-10px 0 10px 0' }}>
                    <img src={LoadingIcon} style={{ width: '50px', height: '100%' }} />
                    <CustomText size='s' weight='bold' justifyContent='flex-start' mx='-1'>hmm .. 생각중</CustomText>
                </Box>
            }
            
            <CustomText size='xs' justifyContent='flex-start' textAlign='start' my='10' mx='25'>
                {displayedText}
            </CustomText>
            <Box sx={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', width: '100%'}}>
                <IconBox onClick={onClickCopy}><img src={CopyIcon} style={{ width: '26px', height: '100%' }} /></IconBox>
                <IconBox onClick={onClickReload}><img src={ReloadIcon} style={{ width: '30px', height: '100%' }} /></IconBox>
            </Box> 
        </CustomContainer>
    );
}
