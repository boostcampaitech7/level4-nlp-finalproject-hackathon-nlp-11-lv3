import React from 'react'
import { styled } from '@mui/system'

const InputBox = styled('input')(
    () => `
    background-color: #212222;
    color: #ffffff;
    font-family: Pretendard-Regular;
    font-size: 18px;
    outline: none;
    border: none;
    border-radius: 25px;
    display: flex;
    width: 90%;
    padding: 0 20px;
    `
)

export default function InputText({ type, placeholder, onChange, autoFocus }) {
    return (
        <InputBox type={type} placeholder={placeholder} onChange={onChange} autoFocus={autoFocus} />
    )
}