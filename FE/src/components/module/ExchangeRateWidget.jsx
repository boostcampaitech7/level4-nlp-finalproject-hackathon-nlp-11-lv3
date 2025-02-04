import React from 'react'
import { styled, Box } from '@mui/system'

import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'

export default function ExchangeRateWidget() {
    return (
    <CustomContainer color='39393B' radius='8' width='85' height='250' my='8'>
        <CustomText size='xs'>환율</CustomText>
    </CustomContainer>
    )
}