import React, { useState, useEffect } from 'react';
import axios from 'axios';
import moment from 'moment';

import { Box } from '@mui/system';
import CustomContainer from '../atom/CustomContainer';
import ExchangeRateBox from './ExchangeRateBox';
import LoadingIcon from '../../assets/icon/spinner_widget.gif'

const LIVE_URL = 'https://api.currencylayer.com/live';
const HISTORICAL_URL = 'https://api.currencylayer.com/historical';
const apiKey = import.meta.env.VITE_EXCHANGERATE_API_KEY;
const historicalApiKey = import.meta.env.VITE_HISTORICAL_EXCHANGERATE_API_KEY;

export default function ExchangeRateWidget() {
  const [rateData, setRateData] = useState({});
  const [yesterdayRateData, setYesterdayRateData] = useState({});
  const [error, setError] = useState(null);
  const [todayLoading, setTodayLoading] = useState(true);
  const [yesterdayloading, setYesterdayLoading] = useState(true);

  async function fetchTodayRate() {
    try {
      const res = await axios.get(LIVE_URL, {
        params: {
          access_key: apiKey,
          currencies: 'KRW,JPY,EUR,CNY',
          source: 'USD',
        }
      })

      if (res.data.success) {
        const usdToKrw = res.data.quotes.USDKRW;
        const jpyToKrw = res.data.quotes.USDJPY ? usdToKrw / res.data.quotes.USDJPY : null;
        const eurToKrw = res.data.quotes.USDEUR ? usdToKrw / res.data.quotes.USDEUR : null;
        const cnyToKrw = res.data.quotes.USDCNY ? usdToKrw / res.data.quotes.USDCNY : null;

        setRateData({
          USD: usdToKrw,
          JPY: jpyToKrw * 100,
          EUR: eurToKrw,
          CNY: cnyToKrw,
        });
      } else {
        throw new Error(res.data.error.info);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setTodayLoading(false);
    }
  }

  async function fetchYesterdayRate() {
    try {
      const res = await axios.get(HISTORICAL_URL, {
        params: {
          access_key: historicalApiKey,
          currencies: 'KRW,JPY,EUR,CNY',
          source: 'USD',
          date: moment().subtract(1, 'days').format('YYYY-MM-DD'),
        }
      })

      if (res.data.success) {     
        const usdToKrw = res.data.quotes.USDKRW;
        const jpyToKrw = res.data.quotes.USDJPY ? usdToKrw / res.data.quotes.USDJPY : null;
        const eurToKrw = res.data.quotes.USDEUR ? usdToKrw / res.data.quotes.USDEUR : null;
        const cnyToKrw = res.data.quotes.USDCNY ? usdToKrw / res.data.quotes.USDCNY : null;

        setYesterdayRateData({
          USD: usdToKrw,
          JPY: jpyToKrw * 100,
          EUR: eurToKrw,
          CNY: cnyToKrw,
        });
      } else {
        throw new Error(res.data.error.info);
      }
    } catch (err) {
      setError(err.message);      
    } finally {
      setYesterdayLoading(false);
    }
  }

  useEffect(() => {
    fetchTodayRate();
    fetchYesterdayRate();
  }, []);

  if (error) {
    return (
      <CustomContainer color='303030' radius='8' width='190px' height='210' my='20px'>
        <Box sx={{ display: 'flex', alignItems: 'center'}}>
          <img src={LoadingIcon} style={{ width: '40px', height: '40px' }} />
        </Box>
      </CustomContainer>
    );
  }

  return (
    <CustomContainer color='303030' radius='8' flexDirection='column' width='190px' height='210' my='20px'>
      <Box sx={{ display: 'flex', justifyContent: 'space-evenly', alignItems: 'center', marginTop: '5px' }}>
        <ExchangeRateBox rate={rateData.USD?.toFixed(2)} yesterdayRate={yesterdayRateData.USD?.toFixed(2)}>USD</ExchangeRateBox>
        <ExchangeRateBox rate={rateData.JPY?.toFixed(2)} yesterdayRate={yesterdayRateData.JPY?.toFixed(2)}>JPY 100</ExchangeRateBox>
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-evenly', alignItems: 'center', marginY: '5px' }}>
        <ExchangeRateBox rate={rateData.EUR?.toFixed(2)} yesterdayRate={yesterdayRateData.EUR?.toFixed(2)}>EUR</ExchangeRateBox>
        <ExchangeRateBox rate={rateData.CNY?.toFixed(2)} yesterdayRate={yesterdayRateData.CNY?.toFixed(2)}>CNY</ExchangeRateBox>
      </Box>
    </CustomContainer>
  );
}
