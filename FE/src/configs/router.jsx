import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Home from '../components/page/home';
import Chat from '../components/page/chat';

export default function RouterConfiguration() {
    return (
        <Routes>
            <Route path='/' element={<Home />} />
            <Route path='/chat' element={<Chat />} />
        </Routes>
    );
}