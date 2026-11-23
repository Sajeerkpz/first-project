package com.selfstudy.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "courses")
public class Course {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 120)
    private String slug;

    @Column(nullable = false, length = 160)
    private String title;

    @Column(nullable = false, length = 3000)
    private String description;

    @Column(nullable = false, length = 80)
    private String category;

    @Column(nullable = false, length = 40)
    private String level;

    @Column(name = "duration_hours", nullable = false)
    private int durationHours;

    @OneToMany(mappedBy = "course")
    private List<Lesson> lessons = new ArrayList<>();

    protected Course() {
    }

    public Course(String slug, String title, String description, String category, String level, int durationHours) {
        this.slug = slug;
        this.title = title;
        this.description = description;
        this.category = category;
        this.level = level;
        this.durationHours = durationHours;
    }

    public Long getId() {
        return id;
    }

    public String getSlug() {
        return slug;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getCategory() {
        return category;
    }

    public String getLevel() {
        return level;
    }

    public int getDurationHours() {
        return durationHours;
    }
}
