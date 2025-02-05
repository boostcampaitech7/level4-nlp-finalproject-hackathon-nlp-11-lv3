import React, { useState, useEffect } from 'react';

import CustomContainer from '../atom/CustomContainer';
import CustomText from '../atom/CustomText';

export default function QueryInput({ children }) {
    const [displayedText, setDisplayedText] = useState('');

    const answer = '현재 기준(2025년 2월 5일) 네이버의 시가총액은 343,016억 원으로 확인됩니다. 이는 한국 IT 산업 내에서 주요 기업으로서의 입지를 반영합니다. 네이버는 안정적인 재무 상태와 성장 가능성을 바탕으로 투자 매력이 있지만, 글로벌 경쟁 심화와 국내 시장 의존도가 도전 과제로 남아 있습니다. 투자를 고려할 경우, 네이버의 AI 기술 개발 및 전자상거래 확장과 같은 성장 동력을 주목하면서도 경쟁 환경과 시장 점유율 변화에 유의해야 합니다.';

    useEffect(() => {
        let index = 0;
        
        const interval = setInterval(() => {
            if (index < answer.length - 1) {
                setDisplayedText((prev) => prev + answer[index]);
                index++;
            } else {
                clearInterval(interval);
            }
        }, 20);

        return () => clearInterval(interval);
    }, [answer]);

    return (
        <CustomContainer color='191A1A' radius='10' width='85' height='auto' flexDirection='column' justifyContent='flex-start' padding='20' my='10'>
            <CustomText color='blur' weight='bold' size='m' justifyContent='flex-start' my='45' mx='5'>
                {children}
            </CustomText>
            
            <CustomText size='s' weight='bold' justifyContent='flex-start' mx='5'>
                💡 답변
            </CustomText>
            
            <CustomText size='xs' justifyContent='flex-start' my='20' mx='25'>
                {displayedText}
            </CustomText>
        </CustomContainer>
    );
}
