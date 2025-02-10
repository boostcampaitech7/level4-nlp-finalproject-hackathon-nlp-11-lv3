import React from 'react'
import { styled, Box } from '@mui/system'

const CustomBox = styled(Box)(
    ({ color, radius, width, height, flexDirection, justifyContent, border, padding, my }) => `
    background-color: #${color};
    color: #ffffff;
    font-family: Pretendard-Regular;
    width: ${width};
    height: ${height}px;
    border-radius: ${radius}px;
    display: flex;
    flex-direction: ${flexDirection};
    justify-content: ${getJustifyContent(justifyContent)};
    alight-items: center;
    margin: ${my} 0 0 0;
    padding: 0 ${padding}px;
    border: ${getBorder(border)};
    `
)

function getBorder(border) {
    if (!!border) return '1px solid #4a4a4a';
    else return 'none';
}

function getJustifyContent(justifyContent) {
    if (!!justifyContent) return justifyContent;
    else return 'center';
}

export default function CustomContainer({ children, type, placeholder, onChange, color, radius, width, height, flexDirection, justifyContent, border, padding, my }) {
    return (
        <CustomBox color={color} radius={radius} width={width} height={height} flexDirection={flexDirection} justifyContent={justifyContent} border={border} padding={padding} my={my} type={type} placeholder={placeholder} onChange={onChange}>{children}</CustomBox>
    )
}