package com.c201.aebook.api.review.persistence.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.c201.aebook.api.review.persistence.entity.ReviewEntity;

@Repository
public interface ReviewRepository extends JpaRepository<ReviewEntity, Long> {
	public ReviewEntity findByUserIdAndBookId(Long userId, Long bookId);

	public Page<ReviewEntity> findByBookId(Long bookId, Pageable pageable);

	public Optional<ReviewEntity> findByIdAndUserId(Long reviewId, Long userId);

	public Page<ReviewEntity> findByUserId(Long userId, Pageable pageable);

	@Query("SELECT RE FROM ReviewEntity RE LEFT JOIN FETCH RE.user ORDER BY RE.updatedAt DESC")
	public List<ReviewEntity> findTop12ByOrderByIdDesc();

}
