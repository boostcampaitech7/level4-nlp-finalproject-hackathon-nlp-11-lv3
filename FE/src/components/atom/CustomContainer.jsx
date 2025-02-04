import React from 'react'
import { styled, Box } from '@mui/system'

const CustomBox = styled(Box)(
    ({ color, radius, width, height, my }) => `
    background-color: #${color};
    color: #ffffff;
    font-family: Pretendard-Regular;
    width: ${width}%;
    height: ${height}px;
    border-radius: ${radius}px;
    display: flex;
    justify-content: center;
    alight-items: center;
    margin: ${my}% 0 0 0;
    padding: 0 20px;
    `
)

export default function CustomContainer({ children, type, placeholder, onChange, color, radius, width, height, my }) {
    return (
        <CustomBox color={color} radius={radius} width={width} height={height} my={my} type={type} placeholder={placeholder} onChange={onChange}>{children}</CustomBox>
    )
}