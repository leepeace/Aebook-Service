package com.c201.book.utils;

import com.c201.book.api.request.ReviewReqDto;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;

/**
 * [문희주] DTO NOT NULL 검증
 */

@Component
public class DtoValidationUtils {

    /**
     * [문희주] ReviewReqDto NOT NULL 검증
     * @param reviewReqDto
     */
    public void validateReviewReqDto(ReviewReqDto reviewReqDto) {
        checkStringType(reviewReqDto.getContent(), "리뷰 내용");
        checkIntType(reviewReqDto.getScore(), "별점");
    }

    public void checkLongType(Long value, String name){
        if(value == null || value <= 0){
            throw new IllegalArgumentException(name + "은/는 필수 입력값이며 양수 값만 가능합니다.");
        }
    }

    public void checkIntType(int value, String name){
        if(value <= 0){
            throw new IllegalArgumentException(name + "은/는 필수 입력값이며 양수 값만 가능합니다.");
        }
    }
    
    public void checkStringType(String value, String name) {
        if(StringUtils.isBlank(value)) {
            throw new IllegalArgumentException(name + "은/는 필수 입력값입니다.");
        }
    }
}
