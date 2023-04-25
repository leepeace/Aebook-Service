package com.c201.aebook.api.story.service.impl;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import com.c201.aebook.api.story.persistence.entity.StoryEntity;
import com.c201.aebook.api.story.persistence.repository.StoryRepository;
import com.c201.aebook.api.story.presentation.dto.response.StoryResponseDTO;
import com.c201.aebook.api.story.service.StoryService;
import com.c201.aebook.api.user.persistence.entity.UserEntity;
import com.c201.aebook.api.user.persistence.repository.UserRepository;
import com.c201.aebook.api.vo.StoryDeleteSO;
import com.c201.aebook.api.vo.StorySO;
import com.c201.aebook.converter.StoryConverter;
import com.c201.aebook.utils.exception.CustomException;
import com.c201.aebook.utils.exception.ErrorCode;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class StoryServiceImpl implements StoryService {
	private final StoryRepository storyRepository;
	private final UserRepository userRepository;
	private final StoryConverter storyConverter;

	@Override
	public void saveStory(StorySO storySO) {
		// 유효한 userId인지 검증
		UserEntity user = userRepository.findById(storySO.getUserId())
			.orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

		storyRepository.save(StoryEntity.builder()
			.title(storySO.getTitle())
			.content(storySO.getContent())
			.imgUrl(storySO.getImgUrl())
			.user(user)
			.build());
	}

	@Override
	public Page<StoryResponseDTO> getStoryList(Long userId, Pageable pageable) {
		// 1. User 유효성 검증
		UserEntity userEntity = userRepository.findById(userId)
			.orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

		// TODO : fetch join이 안되는 관계로 stream 내에서 nickname을 찾는 것으로 임시 구현... 방법 찾기
		Page<StoryEntity> stories = storyRepository.findAllByUserId(userId, pageable);
		return stories.map(storyEntity -> storyConverter.toStoryResponseDTO(storyEntity, storyEntity.getId(),
			userRepository.findById(storyEntity.getUser().getId()).get().getNickname()));
	}

	@Override
	public void deleteStory(StoryDeleteSO storyDeleteSO) {
		// 1. Story 유효성 검증
		StoryEntity storyEntity = storyRepository.findById(storyDeleteSO.getStoryId())
			.orElseThrow(() -> new CustomException(ErrorCode.BOOK_NOT_FOUND));

		// 2. User 유효성 검증
		UserEntity userEntity = userRepository.findById(storyDeleteSO.getUserId())
			.orElseThrow(() -> new CustomException(ErrorCode.USER_NOT_FOUND));

		storyRepository.deleteById(storyDeleteSO.getStoryId());
	}
}
