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

export default function ExchangeRateWidget() {
  const [rateData, setRateData] = useState({});
  const [yesterdayRateData, setYesterdayRateData] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function fetchRates(isYesterday) {
    const url = isYesterday ? HISTORICAL_URL : LIVE_URL;
    const date = isYesterday ? moment().subtract(1, 'days').format('YYYY-MM-DD') : null;

    try {
      const res = await axios.get(url, {
        params: {
          access_key: apiKey,
          currencies: 'KRW,JPY,EUR,CNY',
          source: 'USD',
          ...(isYesterday && { date }),
        },
      });

      if (res.data.success) {
        const usdToKrw = res.data.quotes.USDKRW;
        const jpyToKrw = res.data.quotes.USDJPY ? usdToKrw / res.data.quotes.USDJPY : null;
        const eurToKrw = res.data.quotes.USDEUR ? usdToKrw / res.data.quotes.USDEUR : null;
        const cnyToKrw = res.data.quotes.USDCNY ? usdToKrw / res.data.quotes.USDCNY : null;

        if (isYesterday) {
          setYesterdayRateData({
            USD: usdToKrw,
            JPY: jpyToKrw * 100,
            EUR: eurToKrw,
            CNY: cnyToKrw,
          });
        } else {
          setRateData({
            USD: usdToKrw,
            JPY: jpyToKrw * 100,
            EUR: eurToKrw,
            CNY: cnyToKrw,
          });
        }
      } else {
        throw new Error(res.data.error.info);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchRates(false); // 오늘 환율
    fetchRates(true); // 어제 환율
  }, []);

  if (error || loading) {
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
