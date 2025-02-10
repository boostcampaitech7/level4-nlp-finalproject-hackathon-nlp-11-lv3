import React, { useState, useEffect } from 'react';
import axios from 'axios';
import moment from 'moment';

import CustomText from '../atom/CustomText';
import CustomContainer from '../atom/CustomContainer';

const URL = import.meta.env.VITE_NEWS_API_URL;
const currentDate = moment().format('YYYY-MM-DD');
const oneWeekAgoDate = moment().subtract(7, 'days').format('YYYY-MM-DD');

export default function StockNewsWidget({ company }) {
    const [newsData, setNewsData] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);

    function getNewsSuccess(res) {
        if (res.data.data) {
            setNewsData(res.data.data);
        }
    }

    function getNews() {
        axios
            .get(URL, {
                params: {
                    keyword: `title:${company}`,
                    date_from: oneWeekAgoDate,
                    date_to: currentDate,
                    page_size: '30',
                },
            })
            .then(getNewsSuccess);
    }

    useEffect(() => {
        getNews();
    }, [company]);

    useEffect(() => {
        if (newsData.length > 0) {
            const interval = setInterval(() => {
                setCurrentIndex((prevIndex) => (prevIndex + 1) % newsData.length);
            }, 4000);

            return () => clearInterval(interval);
        }
    }, [newsData]);

    return (
        <CustomContainer color="454545" radius="7" width="190px" height="auto">
            {newsData.length > 0 ? (
                <CustomText size="xxs" mx="15">
                    {'📢' + ' ' + newsData[currentIndex].title}
                </CustomText>
            ) : null}
        </CustomContainer>
    );
}
