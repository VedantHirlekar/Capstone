package com.example.springboot_app.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "employees")   // 🔥 IMPORTANT FIX
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Employee {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String phone;
}