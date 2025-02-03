import React from 'react';
import { styled } from '@mui/system';

const CustomSpan = styled('span')(
    ({ size, color, weight, my, mx }) => `
    font-size: ${getSize(size)};
    color: ${getColor(color)};
    font-family: ${getWeight(weight)};
    margin: ${getMargin(my)}px ${getMargin(mx)}px;
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
            return '#DA5F58';
        case 'down':
            return '#5282CC';
        case 'green':
            return '#395540';
        default:
            return '#ffffff';
    }
}

function getWeight(weight) {
    switch (weight) {
        case 'bold':
            return 'GmarketSansBold';
        case 'light':
            return 'GmarketSansLight';
        default:
            return 'GmarketSansMedium';
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