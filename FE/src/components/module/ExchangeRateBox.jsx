import React from 'react';

import CustomContainer from '../atom/CustomContainer';
import CustomText from '../atom/CustomText';

export default function ExchangeRateBox({ children, rate, yesterdayRate }) {
    const currentRate = parseFloat(rate);
    const previousRate = parseFloat(yesterdayRate);
    const vs = currentRate - previousRate;
    const fltRt = ((currentRate / previousRate) - 1) * 100;

    return (
        <CustomContainer color='white' width='46%' height='95' radius='10' border='y' flexDirection='column'>
            <CustomText size='xxs'>{children}</CustomText>
            <CustomText size='xs' weight='bold'>{currentRate?.toFixed(2)}</CustomText>
            <CustomText size='xxs' color={vs < 0 ? 'down' : 'up'}>
                {vs < 0 ? `▼${Math.abs(vs).toFixed(2)}` : `▲${Math.abs(vs).toFixed(2)}`}
            </CustomText>
            <CustomText size='xxs' color={fltRt < 0 ? 'down' : 'up'}>
                {`${fltRt.toFixed(2)}%`}
            </CustomText>
        </CustomContainer>
    );
}
