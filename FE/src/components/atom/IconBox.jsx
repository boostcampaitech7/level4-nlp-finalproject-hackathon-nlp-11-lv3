import React from 'react';

import { Box } from '@mui/material';

export default function IconBox({ children, onClick }) {
    return (
        <Box onClick={onClick} sx={{ width: '30px', display: 'flex', alignItems: 'center', margin: '20px 5px', cursor: 'pointer', '&:hover': {opacity: 0.6} }}>{children}</Box>
    )
}