import React from 'react'

import { Box } from '@mui/material'
import CustomText from '../atom/CustomText'

export default function StockInfoBox({ text, value, color }) {
    return (
        <Box sx={{ width: '93%', display: 'flex', justifyContent: 'space-between' }}>
            <CustomText size='xxs' color='second' mx='15'>{text}</CustomText>
            <CustomText size='xxs' color={color}>{value}</CustomText>
        </Box>
    )
}