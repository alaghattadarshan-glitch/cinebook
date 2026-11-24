# CINEBOOK – Pure Java OOP Movie Ticket Booking Platform

**CINEBOOK** is an enterprise-grade, full-stack Movie Ticket Booking application built entirely using **pure Java 21**, **Spring Boot 3**, **Spring Data JPA**, and **Thymeleaf**. It demonstrates deep, practical knowledge of **Object-Oriented Programming (OOP) in Java**, dynamic cinema seat layout management, concurrency locking, polymorphic simulated payments, real-time ticket price calculation, and digital scannable QR ticket generation.

---

## 🌟 Key Features

- **100% Pure Java & OOP**: Zero Python dependencies. All models, domain rules, pricing strategies, payment gateways, and controllers are written in modern Java.
- **Interactive Visual Seating Map**: Real-time cinema layout categorizing **Regular**, **Premium**, and **Recliner** luxury seats with live pricing tallies.
- **Seat Concurrency & Double-Booking Prevention**: High-integrity seat locking with automatic 10-minute timeout expirations and atomic database transactions.
- **Recent Indian Blockbusters & Posters**: Featuring the Kannada superhit ***Premada Oorali***, ***Ramayana: Part 1***, ***Pushpa 2: The Rule***, ***Kantara: Chapter 1***, ***KGF: Chapter 2***, and ***Kalki 2898 AD***.
- **Iconic Bengaluru Theatres**: Pre-configured with major Bengaluru multiplexes (*PVR Forum South*, *INOX Mall of Asia*, *Urvashi Cinema 4K RGB Laser*, *Cinepolis VIP Nexus Shantiniketan*).
- **Polymorphic Payment Processing**: Implements `PaymentProcessor` across `UpiPayment` (with VPA validation), `CardPayment` (with masking), and `CashPayment`.
- **Digital Ticket & Verified QR Code**: Auto-generates embedded QR codes encoding verified gate passes for admittance.

---

## 🧩 Deep Dive: Practical OOP Implementation in Java

### 1. Encapsulation
- **Protected State**: Fields like `amount`, `status`, `transactionId` in `BasePayment.java` and `passwordHash` in `BaseUser.java` are protected.
- **Invariant Validation**: `BasePayment.setAmount(double amount)` throws `IllegalArgumentException` if monetary values are non-positive.
- **Concurrency State Verification**: `ShowSeat.isAvailable(sessionId)` dynamically resolves seat availability against expiration timestamps.

### 2. Inheritance
- **User Hierarchy**:
  ```java
  public abstract class BaseUser { ... }
  public class Customer extends BaseUser { ... }
  public class Admin extends BaseUser { ... }
  ```
- **Payment Processing Hierarchy**:
  ```java
  public abstract class BasePayment implements PaymentProcessor { ... }
  public class UpiPayment extends BasePayment { ... }
  public class CardPayment extends BasePayment { ... }
  public class CashPayment extends BasePayment { ... }
  ```

### 3. Polymorphism
- **Uniform Payment Gateway Call**: `PaymentProcessor.processPayment(amount, details)` executes polymorphically across UPI, Card, and Cash without `if/else` checks.
- **Factory Pattern**: `PaymentFactory.createProcessor(method, amount)` instantiates the appropriate polymorphic processor at runtime.
- **Strategy Pattern (Dynamic Ticket Pricing)**:
  - `StandardPricingStrategy`: Flat tiered multipliers (Regular 1.0x, Premium 1.4x, Recliner 2.0x).
  - `WeekendPricingStrategy`: Dynamically introduces a **+20% weekend surge factor** on Friday, Saturday, and Sunday screenings.

### 4. Abstraction
- Pure interfaces `PaymentProcessor` and `PricingStrategy` define strict contracts using Java `interface` specifications.

---

## 🏛️ Project Directory Structure

```
cinebook/
├── pom.xml                               # Maven project definition
├── Dockerfile                            # Java multi-stage container
├── docker-compose.yml                    # Container service definition
└── src/
    └── main/
        ├── java/com/cinebook/
        │   ├── CinebookApplication.java  # Main Spring Boot Entry Point
        │   ├── core/                     # Pure OOP Core
        │   │   ├── PaymentProcessor.java # Abstraction (Interface)
        │   │   ├── BasePayment.java      # Inheritance (Abstract Base)
        │   │   ├── UpiPayment.java       # Polymorphism (UPI)
        │   │   ├── CardPayment.java      # Polymorphism (Card)
        │   │   ├── CashPayment.java      # Polymorphism (Cash)
        │   │   ├── PaymentFactory.java   # Factory Pattern
        │   │   ├── PricingStrategy.java  # Strategy Pattern (Interface)
        │   │   ├── StandardPricingStrategy.java
        │   │   └── WeekendPricingStrategy.java
        │   ├── model/                    # JPA Rich Domain Entities
        │   │   ├── BaseUser.java
        │   │   ├── Customer.java
        │   │   ├── Admin.java
        │   │   ├── Movie.java
        │   │   ├── Theatre.java
        │   │   ├── Screen.java
        │   │   ├── Seat.java
        │   │   ├── Show.java
        │   │   ├── ShowSeat.java         # Concurrency locking model
        │   │   ├── Booking.java          # Master Booking Aggregate
        │   │   ├── BookingSeat.java
        │   │   └── Ticket.java           # Digital pass with QR payload
        │   ├── repository/               # Spring Data JPA Repositories
        │   ├── service/                  # Business Logic Layer
        │   │   ├── BookingService.java   # Seat locking & payment coordinator
        │   │   ├── QrCodeService.java    # Pure Java ZXing QR generator
        │   │   └── DataInitializer.java  # Seed data for movies & Bengaluru venues
        │   └── controller/               # Spring MVC Web Controllers
        │       ├── MovieController.java  # Home & details
        │       └── BookingController.java# Seat map, locking, checkout & ticket
        └── resources/
            ├── application.properties
            ├── templates/                # Thymeleaf HTML Templates
            │   ├── index.html            # Dark Theme Discovery Homepage
            │   ├── movie-details.html    # Showtime selector
            │   ├── seats.html            # Interactive Visual Cinema Seat Map
            │   ├── checkout.html         # Payment selector & bill breakdown
            │   └── ticket.html           # Final Digital Ticket with QR Code
            └── static/                   # CSS, JS, and Movie Posters
```

---

## 🚀 Running CINEBOOK (Java Edition)

The application is already compiled and running on:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**

### How to Build & Run Locally:
```bash
# 1. Compile and package the Java application
./apache-maven-3.9.6/bin/mvn clean package -DskipTests

# 2. Run the JAR file
java -jar target/cinebook-java-1.0.0.jar
```
Open **http://localhost:8080** in your browser.
