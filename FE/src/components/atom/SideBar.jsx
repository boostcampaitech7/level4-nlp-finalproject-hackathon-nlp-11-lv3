import React from 'react';
import { styled, Box } from '@mui/system'

const SideBarBox = styled(Box)(
    () => `
    background-color: #212222;
    width: 300px;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    `
)

export default function SideBar({ children }) {
    return <SideBarBox>{children}</SideBarBox>;
}