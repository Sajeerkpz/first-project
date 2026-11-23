package com.selfstudy.config;

import com.selfstudy.entity.Course;
import com.selfstudy.entity.Lesson;
import com.selfstudy.repository.CourseRepository;
import com.selfstudy.repository.LessonRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SampleDataConfig {
    @Bean
    CommandLineRunner seedCourses(CourseRepository courseRepository, LessonRepository lessonRepository) {
        return args -> {
            if (courseRepository.count() > 0) {
                return;
            }

            Course java = new Course(
                    "java-foundations", "Java Foundations",
                    "Learn the fundamentals of Java, from variables and control flow to object-oriented design.",
                    "Programming", "Beginner", 6);
            Course web = new Course(
                    "web-development", "Web Development Basics",
                    "Understand how HTML, CSS, and JavaScript work together to create useful web pages.",
                    "Web Development", "Beginner", 5);
            Course git = new Course(
                    "git-and-github", "Git and GitHub",
                    "Build a practical workflow for version control, branches, commits, and collaboration.",
                    "Developer Tools", "Beginner", 3);

            courseRepository.saveAll(List.of(java, web, git));
            lessonRepository.saveAll(List.of(
                    new Lesson(java, "Your first Java program", "Java programs are organized into classes. Start with a class containing a main method, then compile and run it with the JDK.", 1),
                    new Lesson(java, "Variables and types", "Use variables to name values. Java has primitive types such as int and boolean, along with reference types such as String.", 2),
                    new Lesson(java, "Conditions and loops", "Use if/else to choose a path and loops to repeat work. Prefer clear loop conditions and small, focused blocks.", 3),
                    new Lesson(java, "Classes and objects", "A class describes state and behavior. Create objects from classes and keep fields private behind a clear public API.", 4),
                    new Lesson(web, "HTML document structure", "HTML gives content meaning. Use semantic elements such as main, nav, section, article, and button where appropriate.", 1),
                    new Lesson(web, "CSS layout and responsive design", "Use Flexbox and Grid for layout. Add responsive breakpoints so content remains usable on small screens.", 2),
                    new Lesson(web, "JavaScript interactions", "JavaScript responds to user actions and updates the page. Attach event listeners and keep behavior separate from markup.", 3),
                    new Lesson(git, "Repository and commits", "A Git repository tracks changes. Stage a focused set of edits and create a commit with a short, descriptive message.", 1),
                    new Lesson(git, "Branches and merging", "Branches let you work on changes independently. Merge a branch after reviewing and resolving any conflicts.", 2),
                    new Lesson(git, "Working with GitHub", "Push a branch to GitHub and open a pull request so changes can be reviewed before they are merged.", 3)
            ));
        };
    }
}
