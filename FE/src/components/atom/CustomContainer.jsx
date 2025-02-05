import React from 'react'
import { styled, Box } from '@mui/system'

const CustomBox = styled(Box)(
    ({ color, radius, width, height, flexDirection, justifyContent, my }) => `
    background-color: #${color};
    color: #ffffff;
    font-family: Pretendard-Regular;
    width: ${width}%;
    height: ${height}px;
    border-radius: ${radius}px;
    display: flex;
    flex-direction: ${flexDirection};
    justify-content: ${getJustifyContent(justifyContent)};
    alight-items: center;
    margin: ${my}% 0 0 0;
    padding: 0 20px;
    `
)

function getJustifyContent(justifyContent) {
    if (!!justifyContent) return justifyContent;
    else return 'center';
}

export default function CustomContainer({ children, type, placeholder, onChange, color, radius, width, height, flexDirection, justifyContent, my }) {
    return (
        <CustomBox color={color} radius={radius} width={width} height={height} flexDirection={flexDirection} justifyContent={justifyContent} my={my} type={type} placeholder={placeholder} onChange={onChange}>{children}</CustomBox>
    )
}