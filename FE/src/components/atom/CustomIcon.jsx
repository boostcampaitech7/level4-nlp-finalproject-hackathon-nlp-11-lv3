import React from 'react'
import { Box } from '@mui/system'

const CustomBox = styled(Box)(
    ({ size }) => `
        width: ${size}px;
        height: ${size}px;
        display: flex;
        justify-content: center;
        align-items: center;
    `
)

export default function CustomIcon({ src, size }) {
    return (
        <CustomBox size={size}>
            <img src={src} style={{ width: '100%', height: '100%' }}/>
        </CustomBox>
    )
}