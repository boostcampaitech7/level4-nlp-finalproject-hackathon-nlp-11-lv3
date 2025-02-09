import React from 'react';
import { Box, styled } from '@mui/system';

const CustomBox = styled(Box)(
    ({ size, color, weight, my, mx, justifyContent, height, textAlign }) => `
    color: ${getColor(color)};
    font-family: ${getWeight(weight)};
    font-size: ${getSize(size)};
    height: ${height};
    margin: ${getMargin(my)}px ${getMargin(mx)}px;
    display: flex;
    align-items: center;
    justify-content: ${getJustifyContent(justifyContent)};
    text-align: ${getTextAlign(textAlign)};
    `
);

function getSize(size) {
    switch (size) {
        case 'xxl':
            return '35px';
        case 'xl':
            return '33px';
        case 'l':
            return '30px';
        case 'm':
            return '23px';
        case 's':
            return '18px';
        case 'xs':
            return '15px';
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
        case 'blur':
            return '#A1A1A1';
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

function getJustifyContent(justifyContent) {
    if (!!justifyContent) return justifyContent;
    else return 'center';
}

function getTextAlign(textAlign) {
    if (!!textAlign) return textAlign;
    else return 'center';
}

export default function CustomText({ children, size, color, weight, my, mx, justifyContent, textAlign, height }) {
    return (
        <CustomBox size={size} color={color} weight={weight} my={my} mx={mx} justifyContent={justifyContent} textAlign={textAlign} height={height}>
            {children}
        </CustomBox>
    )
}