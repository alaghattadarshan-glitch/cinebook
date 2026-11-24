package com.cinebook.model;

import jakarta.persistence.DiscriminatorValue;
import jakarta.persistence.Entity;

@Entity
@DiscriminatorValue("ADMIN")
public class Admin extends BaseUser {
    public Admin() {}
    public Admin(String name, String email, String password) {
        super(name, email, password);
    }
    @Override
    public boolean isAdmin() { return true; }
}
