import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Main from '../components/page/main';
import Chat from '../components/page/chat';

export default function RouterConfiguration() {
    return (
        <Routes>
            <Route path='/' element={<Main />} />
            <Route path='/chat' element={<Chat />} />
        </Routes>
    );
}