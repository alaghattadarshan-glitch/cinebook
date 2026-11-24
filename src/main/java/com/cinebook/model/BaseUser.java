package com.cinebook.model;

import jakarta.persistence.*;

/**
 * Demonstrates:
 * 1. Inheritance: BaseUser -> Customer, Admin
 * 2. Encapsulation: Protected passwords, validation
 */
@Entity
@Table(name = "users")
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "user_role")
public abstract class BaseUser {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    protected String name;

    @Column(nullable = false, unique = true)
    protected String email;

    @Column(nullable = false)
    protected String passwordHash;

    public BaseUser() {}

    public BaseUser(String name, String email, String passwordHash) {
        this.name = name;
        this.email = email;
        this.passwordHash = passwordHash;
    }

    public Long getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }

    public abstract boolean isAdmin();
}
