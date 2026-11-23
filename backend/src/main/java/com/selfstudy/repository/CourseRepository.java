package com.selfstudy.repository;

import com.selfstudy.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CourseRepository extends JpaRepository<Course, Long> {
    List<Course> findAllByOrderByIdAsc();
    Optional<Course> findBySlug(String slug);
}
