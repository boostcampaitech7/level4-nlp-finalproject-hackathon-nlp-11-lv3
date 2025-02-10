import express from 'express';
import axios from 'axios';
import cors from 'cors';

const app = express();
const PORT = 3001;

const URL = 'https://api-v2.deepsearch.com/v1/articles/economy';
const apiKey = import.meta.env.VITE_NEWS_API_KEY;

app.use(cors());

app.get('/api/news', async (req, res) => {
  const { keyword, date_from, date_to, page_size } = req.query;

  try {
    const response = await axios.get(URL, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      params: { keyword, date_from, date_to, page_size},
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error fetching news:', error);
    res.status(500).json({ error: 'Failed to fetch news' });
  }
});

app.listen(PORT, () => {
  console.log(`Proxy server is running on http://localhost:${PORT}`);
});
