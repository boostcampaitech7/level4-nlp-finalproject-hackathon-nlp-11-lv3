import React from 'react';

import { Box } from '@mui/material';

export default function SelectModel({ onModelChange, selectedValue }) {
    function handleChange(e) {
        if (onModelChange) {
            onModelChange(e.target.value);
        }
    }

    return (
        <Box sx={{ display: 'flex', width: '84%', marginTop: '10px', justifyContent: 'flex-end' }}>
            <Box sx={{ width: '115px', color: '#AAAAAA' }}>
                <select className='select w-full max-w-xs' onChange={handleChange} value={selectedValue || ''}>
                    <option value='' disabled >모델 선택</option>
                    <option value='GPT-4o'>GPT-4o</option>
                    <option value='GPT-4o mini'>GPT mini</option>
                    <option value='CLOVA X'>CLOVA X</option>
                </select>
            </Box>
        </Box>
    );
}
