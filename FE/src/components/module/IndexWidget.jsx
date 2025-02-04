import React from 'react'
import axios from 'axios'
import moment from 'moment'

import { Box } from '@mui/system'
import CustomText from '../atom/CustomText'
import CustomContainer from '../atom/CustomContainer'

const URL = 'https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex';
const apiKey = import.meta.env.VITE_Index_API_KEY;
const currentDate = moment().format('YYYYMMDD');

function getIndexSuccess(res) {
  const data = res.data.response.body.items.item[0];
  const basDt = data.basDt; // 날짜
  const clpr = data.clpr; // 종가
  const hipr = data.hipr; // 고가
  const lopr = data.lopr; // 저가
  const vs = data.vs; // 전일대비
  const fltRt = data.fltRt;

  // console.log(basDt, clpr, hipr, lopr, vs, fltRt);
}

function getIndex() {
  axios
    .get(
      URL,
      {
        params: {
          serviceKey: apiKey,
          resultType: 'json',
          baseDt: currentDate,
          idxNm: "코스피"
        }
      }
    )
    .then(getIndexSuccess);
}

export default function IndexWidget() {
    return (
      <Box onClick={getIndex} sx={{ display: 'flex', width: '85%', cursor: 'pointer' }}>
        <CustomContainer color='39393B' radius='8' width='100' height='250' my='90'>
          <CustomText size='xs'>지수</CustomText>
        </CustomContainer>
      </Box>
    )
}