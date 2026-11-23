package com.selfstudy.repository;

import com.selfstudy.entity.LessonProgress;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface LessonProgressRepository extends JpaRepository<LessonProgress, Long> {
    boolean existsByUser_IdAndLesson_Id(Long userId, Long lessonId);
    List<LessonProgress> findByUser_Id(Long userId);
    long countByUser_IdAndLesson_Course_Id(Long userId, Long courseId);
}
