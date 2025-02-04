import React from 'react';
import { styled } from '@mui/system';

const CustomSpan = styled('span')(
    ({ size, color, weight, my, mx }) => `
    color: ${getColor(color)};
    font-family: ${getWeight(weight)};
    font-size: ${getSize(size)};
    margin: ${getMargin(my)}px ${getMargin(mx)}px;
    display: flex;
    `
);

function getSize(size) {
    switch (size) {
        case 'xxl':
            return '50px';
        case 'xl':
            return '40px';
        case 'l':
            return '35px';
        case 'm':
            return '30px';
        case 's':
            return '20px';
        case 'xs':
            return '16px';
        case 'xxs':
            return '13px';
        default:
            return '20px';
    }
}

function getColor(color) {
    switch (color) {
        case 'primary':
            return '#ffffff';
        case 'second':
            return '#7A7A7C';
        case 'up':
            return '#E43332';
        case 'down':
            return '#3871CA';
        case 'green':
            return '#37824A';
        default:
            return '#ffffff';
    }
}

function getWeight(weight) {
    switch (weight) {
        case 'bold':
            return 'Pretendard-Bold';
        case 'light':
            return 'Pretendard-Light';
        default:
            return 'Pretendard-Regular';
    }    
}

function getMargin(px) {
    if (!!px) return px;
    else return 0;
}

export default function CustomText({ children, size, color, weight, my, mx }) {
    return (
        <CustomSpan size={size} color={color} weight={weight} my={my} mx={mx}>
            {children}
        </CustomSpan>
    )
}