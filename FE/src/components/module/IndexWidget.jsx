import React, { useState, useEffect } from 'react'
import axios from 'axios'
import moment from 'moment'

import { Box } from '@mui/system'
import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'

const URL = 'https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex';
const apiKey = import.meta.env.VITE_INDEX_API_KEY;
const currentDate = moment().format('YYYYMMDD');

export default function IndexWidget() {
  const [indexData, setIndexData] = useState();

  function getIndexSuccess(res) {
    const data = res.data.response.body.items.item[0];

    if (!data || data.length === 0) {      
      console.error('No data found in API response');
      return;
    }

    setIndexData({
      basDt: data.basDt, // 날짜
      clpr: data.clpr, // 종가
      hipr: data.hipr, // 고가
      lopr: data.lopr, // 저가
      vs: data.vs, // 전일 대비
      fltRt: data.fltRt, // 등락률
    });
  }

  function getIndex() {
    axios
      .get(
        URL,
        {
          params: {
            serviceKey: apiKey,
            resultType: 'json',
            endBasDt: currentDate,
            idxNm: '코스피'
          }
        }
      )
      .then(getIndexSuccess);
  } 

  useEffect(() => {
    getIndex();
  }, [])

  return (
    <Box sx={{ display: 'flex', width: '80%', cursor: 'pointer' }}>
      {indexData ? (
        <CustomContainer color='303032' radius='8' width='100' height='210' flexDirection='column' my='90'>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end' }}>
            <CustomText size='s' weight='bold' mx='5'>KOSPI</CustomText>
            <CustomText size='xxs' color='second' my='2' mx='4'>{`${indexData.basDt.slice(4, 6)}.${indexData.basDt.slice(6)}`}</CustomText>
          </Box>
          <CustomText size='l' weight='bold'>{`${indexData.clpr}`}</CustomText>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end' }}>
            <CustomText size='xs' weight='bold' color={parseFloat(indexData.vs) < 0 ? 'down' : 'up'} mx='6'>{parseFloat(indexData.vs) < 0 ? `▼ ${indexData.vs.slice(1,)}` : `▲ ${indexData.vs}`}</CustomText>
            <CustomText size='xs' weight='bold' color={parseFloat(indexData.fltRt) < 0 ? 'down' : 'up'} mx='6'>{`${indexData.fltRt}%`}</CustomText>
          </Box>
        </CustomContainer>
      ) : (
        <CustomContainer color='303032' radius='8' width='100' height='250' flexDirection='column' my='90'>
          <CustomText size='xs'>Loading...</CustomText>
        </CustomContainer>
      )}
    </Box>
  );
}