# PadelGo Monorepo

This repository contains the full source code for the PadelGo application, including the backend API, the user-facing web application, and the club administrator portal.

## Project Overview

For a detailed overview of the project's architecture, tech stack, and services, please see the [Project Overview document](./PROJECT_OVERVIEW.md).

## Getting Started

To get started with the development environment, you will need to have Node.js, pnpm, and Python installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tarikstafford/PadelApp.git
    cd PadelApp
    ```

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```

3.  **Set up the backend:**
    *   Create a `.env` file in the `padel-app/apps/api` directory with the necessary environment variables.
    *   Run the database migrations: `pnpm --filter api run migrate`
    *   Start the backend server: `pnpm --filter api run dev`

4.  **Set up the frontend:**
    *   **Web App:** `pnpm --filter web run dev`
    *   **Club Admin App:** `pnpm --filter club-admin run dev` 