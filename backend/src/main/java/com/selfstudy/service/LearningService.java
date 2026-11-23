package com.selfstudy.service;

import com.selfstudy.entity.Course;
import com.selfstudy.entity.Enrollment;
import com.selfstudy.entity.Lesson;
import com.selfstudy.entity.LessonProgress;
import com.selfstudy.entity.User;
import com.selfstudy.repository.CourseRepository;
import com.selfstudy.repository.EnrollmentRepository;
import com.selfstudy.repository.LessonProgressRepository;
import com.selfstudy.repository.LessonRepository;
import com.selfstudy.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class LearningService {
    private final CourseRepository courseRepository;
    private final LessonRepository lessonRepository;
    private final EnrollmentRepository enrollmentRepository;
    private final LessonProgressRepository progressRepository;
    private final UserRepository userRepository;

    public LearningService(
            CourseRepository courseRepository,
            LessonRepository lessonRepository,
            EnrollmentRepository enrollmentRepository,
            LessonProgressRepository progressRepository,
            UserRepository userRepository
    ) {
        this.courseRepository = courseRepository;
        this.lessonRepository = lessonRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.progressRepository = progressRepository;
        this.userRepository = userRepository;
    }

    public List<CourseSummary> listCourses(User currentUser) {
        Set<Long> enrolledCourseIds = currentUser == null
                ? Set.of()
                : enrollmentRepository.findByUser_IdOrderByEnrolledAtDesc(currentUser.getId())
                        .stream().map(enrollment -> enrollment.getCourse().getId()).collect(Collectors.toSet());
        return courseRepository.findAllByOrderByIdAsc().stream()
                .map(course -> summary(course, currentUser, enrolledCourseIds.contains(course.getId())))
                .toList();
    }

    public CourseDetail courseDetails(String slug, User currentUser) {
        Course course = findCourse(slug);
        boolean enrolled = currentUser != null
                && enrollmentRepository.existsByUser_IdAndCourse_Id(currentUser.getId(), course.getId());
        Set<Long> completedLessonIds = currentUser == null || !enrolled
                ? Set.of()
                : progressRepository.findByUser_Id(currentUser.getId()).stream()
                        .map(progress -> progress.getLesson().getId()).collect(Collectors.toSet());
        List<LessonItem> lessons = lessonRepository.findByCourse_IdOrderByPositionAsc(course.getId()).stream()
                .map(lesson -> new LessonItem(
                        lesson.getId(), lesson.getTitle(), lesson.getPosition(),
                        enrolled ? lesson.getContent() : null,
                        completedLessonIds.contains(lesson.getId())))
                .toList();

        return new CourseDetail(
                course.getId(), course.getSlug(), course.getTitle(), course.getDescription(),
                course.getCategory(), course.getLevel(), course.getDurationHours(),
                enrolled, lessons.size(), lessons, progressPercent(completedLessonIds.size(), lessons.size()));
    }

    @Transactional
    public void enroll(String slug, User currentUser) {
        Course course = findCourse(slug);
        if (!enrollmentRepository.existsByUser_IdAndCourse_Id(currentUser.getId(), course.getId())) {
            enrollmentRepository.save(new Enrollment(currentUser, course));
        }
    }

    @Transactional
    public void completeLesson(Long lessonId, User currentUser) {
        Lesson lesson = lessonRepository.findById(lessonId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Lesson not found"));
        Long courseId = lesson.getCourse().getId();
        if (!enrollmentRepository.existsByUser_IdAndCourse_Id(currentUser.getId(), courseId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Enroll in this course before completing lessons");
        }
        if (!progressRepository.existsByUser_IdAndLesson_Id(currentUser.getId(), lessonId)) {
            progressRepository.save(new LessonProgress(currentUser, lesson));
        }
    }

    public Dashboard dashboard(User currentUser) {
        List<Enrollment> enrollments = enrollmentRepository.findByUser_IdOrderByEnrolledAtDesc(currentUser.getId());
        List<CourseProgress> courses = enrollments.stream().map(enrollment -> {
            Course course = enrollment.getCourse();
            long total = lessonRepository.countByCourse_Id(course.getId());
            long completed = progressRepository.countByUser_IdAndLesson_Course_Id(currentUser.getId(), course.getId());
            return new CourseProgress(
                    course.getId(), course.getSlug(), course.getTitle(), course.getCategory(),
                    course.getLevel(), course.getDurationHours(), total, completed,
                    progressPercent(completed, total));
        }).toList();
        return new Dashboard(currentUser.getName(), courses);
    }

    private Course findCourse(String slug) {
        return courseRepository.findBySlug(slug)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Course not found"));
    }

    private CourseSummary summary(Course course, User currentUser, boolean enrolled) {
        long total = lessonRepository.countByCourse_Id(course.getId());
        long completed = currentUser != null && enrolled
                ? progressRepository.countByUser_IdAndLesson_Course_Id(currentUser.getId(), course.getId())
                : 0;
        return new CourseSummary(
                course.getId(), course.getSlug(), course.getTitle(), course.getDescription(),
                course.getCategory(), course.getLevel(), course.getDurationHours(), total,
                enrolled, completed, progressPercent(completed, total));
    }

    private int progressPercent(long completed, long total) {
        return total == 0 ? 0 : (int) Math.round(completed * 100.0 / total);
    }

    public record CourseSummary(
            Long id, String slug, String title, String description, String category,
            String level, int durationHours, long lessonCount, boolean enrolled,
            long completedLessons, int progressPercent
    ) {
    }

    public record LessonItem(Long id, String title, int position, String content, boolean completed) {
    }

    public record CourseDetail(
            Long id, String slug, String title, String description, String category,
            String level, int durationHours, boolean enrolled, int lessonCount,
            List<LessonItem> lessons, int progressPercent
    ) {
    }

    public record CourseProgress(
            Long id, String slug, String title, String category, String level,
            int durationHours, long lessonCount, long completedLessons, int progressPercent
    ) {
    }

    public record Dashboard(String name, List<CourseProgress> courses) {
    }
}
