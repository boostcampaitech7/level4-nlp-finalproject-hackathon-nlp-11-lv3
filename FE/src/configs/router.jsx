import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import MainPage from '../components/page/MainPage';
import ChatPage from '../components/page/ChatPage';

export default function RouterConfiguration() {
    return (
        <Routes>
            <Route path='/' element={<MainPage />} />
            <Route path='/chat' element={<ChatPage />} />
        </Routes>
    );
}