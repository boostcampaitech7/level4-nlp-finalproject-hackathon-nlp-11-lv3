import React from 'react';

import { styled, Box } from '@mui/system'

const SideBarBox = styled(Box)(
    () => `
    background-color: #212222;
    width: 280px;
    height: 100vh;
    display: flex;
    // flex-direction: column;
    `
)

export default function SideBar({ children }) {
    return <SideBarBox>{children}</SideBarBox>;
}