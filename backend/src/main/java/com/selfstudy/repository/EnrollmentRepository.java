package com.selfstudy.repository;

import com.selfstudy.entity.Enrollment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {
    boolean existsByUser_IdAndCourse_Id(Long userId, Long courseId);
    List<Enrollment> findByUser_IdOrderByEnrolledAtDesc(Long userId);
}
