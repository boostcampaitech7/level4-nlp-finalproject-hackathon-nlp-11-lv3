import axios from 'axios'

const authorization = btoa('test@email.com:1234');

const api = axios.create({
    baseURL: 'http://10.28.224.90:30685/api/',
    headers: {
        'Authorization': `Basic ${authorization}`,
        'Content-Type': 'application/json',
    }
});

export default api;