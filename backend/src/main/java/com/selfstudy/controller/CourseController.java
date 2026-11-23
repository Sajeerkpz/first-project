package com.selfstudy.controller;

import com.selfstudy.entity.User;
import com.selfstudy.service.LearningService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/courses")
public class CourseController {
    private final LearningService learningService;

    public CourseController(LearningService learningService) {
        this.learningService = learningService;
    }

    @GetMapping
    public List<LearningService.CourseSummary> list(Authentication authentication) {
        return learningService.listCourses(currentUser(authentication));
    }

    @GetMapping("/{slug}")
    public LearningService.CourseDetail details(
            @PathVariable String slug,
            Authentication authentication
    ) {
        return learningService.courseDetails(slug, currentUser(authentication));
    }

    @PostMapping("/{slug}/enroll")
    public ResponseEntity<Map<String, String>> enroll(
            @PathVariable String slug,
            Authentication authentication
    ) {
        learningService.enroll(slug, (User) authentication.getPrincipal());
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("message", "You are enrolled"));
    }

    private User currentUser(Authentication authentication) {
        return authentication != null && authentication.getPrincipal() instanceof User user ? user : null;
    }
}
