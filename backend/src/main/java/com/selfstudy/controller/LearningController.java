package com.selfstudy.controller;

import com.selfstudy.entity.User;
import com.selfstudy.service.LearningService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class LearningController {
    private final LearningService learningService;

    public LearningController(LearningService learningService) {
        this.learningService = learningService;
    }

    @GetMapping("/me/dashboard")
    public LearningService.Dashboard dashboard(Authentication authentication) {
        return learningService.dashboard((User) authentication.getPrincipal());
    }

    @PostMapping("/lessons/{lessonId}/complete")
    public ResponseEntity<Map<String, String>> completeLesson(
            @PathVariable Long lessonId,
            Authentication authentication
    ) {
        learningService.completeLesson(lessonId, (User) authentication.getPrincipal());
        return ResponseEntity.ok(Map.of("message", "Lesson marked complete"));
    }
}
