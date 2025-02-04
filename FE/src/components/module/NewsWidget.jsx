import React from 'react'
import { styled, Box } from '@mui/system'

import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'

export default function NewsWidget() {
    return (
    <CustomContainer color='39393B' radius='8' width='100' height='35'>
        <CustomText size='xs'>트럼프 한마디에 울고 웃다</CustomText>
    </CustomContainer>
    )
}