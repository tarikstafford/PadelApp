# PadelGo Project Overview

This document provides a comprehensive overview of the PadelGo project, including its architecture, tech stack, services, and core use cases.

## 1. High-Level Architecture

The PadelGo project is a modern web application built using a **monorepo architecture**. This means that all the code for the different parts of the application (backend, frontend, shared libraries) is stored in a single repository. This approach simplifies dependency management and promotes code sharing.

The project is composed of three main services:

*   **`padelgo-backend`:** A FastAPI backend that serves as the central API for the entire application.
*   **`padelgo-frontend`:** A Next.js application that serves as the main user-facing website for players.
*   **`club-admin`:** A separate Next.js application that serves as a dedicated portal for club administrators.

All three services are deployed on **Railway**, a modern cloud platform that simplifies infrastructure management.

## 2. Tech Stack

The project utilizes a modern and robust tech stack, with a clear separation between the frontend and backend technologies.

### 2.1. Backend (`padelgo-backend`)

*   **Framework:** **FastAPI**, a high-performance Python web framework for building APIs.
*   **Database:** **PostgreSQL**, a powerful open-source relational database.
*   **ORM:** **SQLAlchemy**, a comprehensive SQL toolkit and Object-Relational Mapper (ORM) for Python.
*   **Migrations:** **Alembic**, a lightweight database migration tool for SQLAlchemy.
*   **Authentication:** **`passlib`** with **`bcrypt`** for password hashing and **JWT** for token-based authentication.
*   **Validation:** **Pydantic** is used extensively for data validation and settings management.

### 2.2. Frontend (`padelgo-frontend` & `club-admin`)

*   **Framework:** **Next.js**, a popular React framework for building server-rendered and statically generated web applications.
*   **Language:** **TypeScript**, a statically typed superset of JavaScript that enhances code quality and maintainability.
*   **UI Components:** **`shadcn/ui`**, a collection of beautifully designed, accessible, and composable React components.
*   **Styling:** **Tailwind CSS**, a utility-first CSS framework for rapid UI development.
*   **State Management:**
    *   **`react-hook-form`** and **`zod`** are used for efficient and type-safe form management.
    *   **React Context API** is used for managing global state, such as authentication.

## 3. Services Deep Dive

### 3.1. `padelgo-backend`

The backend is a well-structured FastAPI application with a clear separation of concerns.

*   **Data Models (`app/models`):** Defines the database schema using SQLAlchemy models. Key models include `User`, `Club`, `Court`, `Booking`, and `Game`.
*   **API Routers (`app/routers`):** Exposes the application's functionality through a set of API endpoints. There are dedicated routers for authentication (`auth`), clubs, courts, bookings, games, and a protected `admin` router for club administrator actions.
*   **CRUD Operations (`app/crud`):** Contains the functions that interact with the database, separating the business logic from the database queries.
*   **Schemas (`app/schemas`):** Uses Pydantic models to define the shape of the data for API requests and responses, ensuring data consistency and validation.

### 3.2. `padelgo-frontend`

This is the main application for players. It allows them to find clubs, view courts, and book games. It shares a common UI library with the `club-admin` app to ensure a consistent look and feel.

### 3.3. `club-admin`

This is a dedicated portal for club administrators. It provides a comprehensive set of tools for managing a padel club.

*   **Authentication:** The portal has its own login and registration flow, which creates users with a `CLUB_ADMIN` role.
*   **Club Management:** Admins can view and update their club's profile information, including a profile photo.
*   **Court Management:** A full CRUD interface for managing the club's courts.
*   **Booking Viewer:** A read-only view of all bookings for the club's courts, with filtering and pagination.
*   **Landing Page:** A public-facing landing page that markets the features of the admin portal to potential new clubs.
*   **Onboarding:** A multi-step registration flow to guide new admins through the process of creating their account and their club.

### 3.4. `@workspace/ui` (Shared Component Library)

This is a dedicated package within the monorepo that contains all the shared `shadcn/ui` components. This ensures that both the `padelgo-frontend` and `club-admin` applications have a consistent design system and reduces code duplication.

## 4. Core Use Cases

The PadelGo project is designed to serve two primary user groups: **Players** and **Club Admins**.

### 4.1. For Players (Handled by `padelgo-frontend`)

*   Browse and discover padel clubs.
*   View details about clubs and their courts.
*   Create an account and log in.
*   Book courts for specific time slots.
*   Create and join games with other players.

### 4.2. For Club Admins (Handled by `club-admin`)

*   Register their club and create an admin account.
*   Manage their club's profile, including contact information and photos.
*   Add, edit, and delete courts.
*   View all bookings for their club.
*   (Future) Manage players and accept payments.

This document provides a complete picture of the PadelGo project's architecture and functionality. The use of a monorepo, a modern tech stack, and a clear separation of services creates a robust and scalable foundation for future development. 

## 5. Design

We use shadcn components to build out most of the ui/ux. Add feedback for users if things go well or they go wrong!