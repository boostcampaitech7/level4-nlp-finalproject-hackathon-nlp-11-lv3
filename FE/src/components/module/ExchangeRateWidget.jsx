import React, { useState, useEffect } from 'react'
import axios from 'axios'

import { styled, Box } from '@mui/system'
import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'

const URL = ''
const apiKey = import.meta.env.VITE_ExchangeRate_API_KEY;

export default function ExchangeRateWidget() {
    const [ERData, setERDate] = useState();

    function getERSuccess(res) {
        // const data = ;
    }

    return (
    <CustomContainer color='303032' radius='8' width='80' height='210' my='8'>
        <CustomText size='xs'>환율</CustomText>
    </CustomContainer>
    )
}