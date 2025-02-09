import React, { useState, useEffect } from 'react'
import axios from 'axios'
import moment from 'moment'

import { Box } from '@mui/system'
import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'
import StockInfoBox from './StockInfoBox'
import LoadingIcon from '../../assets/icon/spinner_widget.gif'

const URL = 'https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo';
const apiKey = import.meta.env.VITE_STOCK_API_KEY;
const currentDate = moment().format('YYYYMMDD');

export default function StockWidget( { company }) {
  const [stockData, setStockData] = useState();

  function getStockSuccess(res) {
    const data = res.data.response.body.items.item[0];

    if (!data || data.length === 0) {      
      console.error('No data found in API response');
      return;
    }

    setStockData({
      itmsNm: data.itmsNm, // 종목명
      basDt: data.basDt, // 날짜
      srtnCd: data.srtnCd, // 종목코드
      mrktCtg: data.mrktCtg, // 시장구분
      mkp: data.mkp, // 시가
      clpr: data.clpr, // 종가
      hipr: data.hipr, // 고가
      lopr: data.lopr, // 저가
      vs: data.vs, // 전일 대비
      fltRt: data.fltRt, // 등락률
      mrktTotAmt: data.mrktTotAmt, // 시가총액
      trqu: data.trqu, // 거래량
      yesterdayClpr: res.data.response.body.items.item[1].clpr,
    });
  }

  function getStock() {
    axios.get(URL, {
      params: {
        serviceKey: apiKey,
        resultType: 'json',
        endBasDt: currentDate,
        likeItmsNm: company,
        numOfRows: 2,
        pageNo: 1,
      } 
    })
    .then(getStockSuccess);
  } 

  useEffect(() => {
    getStock();
  }, [company])

  return (
    <Box sx={{ display: 'flex', width: '100%', flexDirection: 'column', alignItems: 'center' }}>
      {stockData ? (
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <CustomContainer color='303030' radius='8' width='190px' height='210' flexDirection='column' my='105px'>
            <CustomText weight='bold' my='-8'>{stockData.itmsNm}</CustomText>
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end' }}>
              <CustomText size='xxs' color='second' mx='4'>{stockData.srtnCd}</CustomText>
              <CustomText size='xxs' color='second' mx='4'>{stockData.mrktCtg}</CustomText>
            </Box>
            <CustomText size='l' weight='bold'>{`${new Intl.NumberFormat().format(stockData.clpr)}`}</CustomText>
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end' }}>
              <CustomText size='xs' weight='bold' color={parseFloat(stockData.vs) < 0 ? 'down' : 'up'} mx='6'>{parseFloat(stockData.vs) < 0 ? `▼ ${new Intl.NumberFormat().format(stockData.vs.slice(1,))}` : `▲ ${new Intl.NumberFormat().format(stockData.vs)}`}</CustomText>
              <CustomText size='xs' weight='bold' color={parseFloat(stockData.fltRt) < 0 ? 'down' : 'up'} mx='6'>{`${stockData.fltRt}%`}</CustomText>
            </Box>
          </CustomContainer>       

          <CustomContainer color='303030' radius='8' width='190px' height='210' flexDirection='column' justifyContent='flex-start' my='20px'>
            <CustomText size='s' weight='bold' my='10' textAlign='start'>시세정보</CustomText>
            <StockInfoBox text='시가' value={new Intl.NumberFormat().format(stockData.mkp)} color={stockData.yesterdayClpr < stockData.mkp ? 'up' : 'down'} />
            <StockInfoBox text='오늘 최고' value={new Intl.NumberFormat().format(stockData.hipr)} color={stockData.yesterdayClpr < stockData.hipr ? 'up' : 'down'} />
            <StockInfoBox text='오늘 최저' value={new Intl.NumberFormat().format(stockData.lopr)} color={stockData.yesterdayClpr < stockData.lopr ? 'up' : 'down'} />
            <CustomText size='s' weight='bold' my='10'>종목정보</CustomText>
            <StockInfoBox text='시가 총액(억원)' value={new Intl.NumberFormat().format(stockData.mrktTotAmt.slice(0,-8))} />
            <StockInfoBox text='거래량' value={new Intl.NumberFormat().format(stockData.trqu)} />
          </CustomContainer> 
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column' }}>
          <CustomContainer color='303030' radius='8' width='190px' height='210' my='105px'>
            <Box sx={{ display: 'flex', alignItems: 'center'}}>
              <img src={LoadingIcon} style={{ width: '40px', height: '40px' }} />
            </Box>
          </CustomContainer>
          <CustomContainer color='303030' radius='8' width='190px' height='210' my='20px'>
            <Box sx={{ display: 'flex', alignItems: 'center'}}>
              <img src={LoadingIcon} style={{ width: '40px', height: '40px' }} />
            </Box>
          </CustomContainer>
        </Box>
      )}
    </Box>
  );
}