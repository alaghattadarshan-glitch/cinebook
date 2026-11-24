package com.cinebook.model;

import jakarta.persistence.DiscriminatorValue;
import jakarta.persistence.Entity;

@Entity
@DiscriminatorValue("CUSTOMER")
public class Customer extends BaseUser {
    public Customer() {}
    public Customer(String name, String email, String password) {
        super(name, email, password);
    }
    @Override
    public boolean isAdmin() { return false; }
}
