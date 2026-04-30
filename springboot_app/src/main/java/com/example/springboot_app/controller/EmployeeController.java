package com.example.springboot_app.controller;

import com.example.springboot_app.model.Employee;
import com.example.springboot_app.repository.EmployeeRepository;
import org.springframework.web.bind.annotation.*;

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;

@RestController
@RequestMapping("/employees")
public class EmployeeController {

    private final EmployeeRepository repo;

    public EmployeeController(EmployeeRepository repo) {
        this.repo = repo;
    }

    // 🔥 GET
    @GetMapping
    public List<Employee> getAll(HttpServletRequest request) {
        long start = System.currentTimeMillis();

        System.out.println("🔥 SPRINGBOOT HIT → GET " + request.getRequestURI());

        List<Employee> result = repo.findAll();

        System.out.println("✅ SPRINGBOOT RESPONSE → GET " 
            + request.getRequestURI() + " | 200 | " 
            + (System.currentTimeMillis() - start) + "ms");

        return result;
    }

    // 🔥 POST
    @PostMapping
    public Employee add(@RequestBody Employee emp, HttpServletRequest request) {
        long start = System.currentTimeMillis();

        System.out.println("🔥 SPRINGBOOT HIT → POST " + request.getRequestURI());
        System.out.println("📦 Body: name=" + emp.getName() + ", phone=" + emp.getPhone());

        Employee saved = repo.save(emp);

        System.out.println("✅ SPRINGBOOT RESPONSE → POST " 
            + request.getRequestURI() + " | 200 | " 
            + (System.currentTimeMillis() - start) + "ms");

        return saved;
    }
}