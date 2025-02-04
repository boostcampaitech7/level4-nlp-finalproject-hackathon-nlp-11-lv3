import React from 'react'
import { styled, Box } from '@mui/system'

const CustomBox = styled(Box)(
    () => `
    background-color: #212222;
    color: #ffffff;
    font-family: Pretendard-Regular;
    font-size: 17px;
    width: 85%;
    height: 140px;
    border-radius: 25px;
    display: flex;
    alight-items: center;
    justify-content: space-evenly;
    padding: 0 20px;
    `
)

export default function CustomSpace({ children, type, placeholder, onChange }) {
    return (
        <CustomBox type={type} placeholder={placeholder} onChange={onChange}>{children}</CustomBox>
    )
}