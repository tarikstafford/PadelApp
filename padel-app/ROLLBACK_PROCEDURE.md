# Cloudinary Integration Rollback Plan

This document outlines the procedure for rolling back the Cloudinary integration to the previous local file storage implementation in case of critical issues.

## 1. Decision Matrix

A rollback should be considered if:

- There is a critical failure in the Cloudinary service that affects all image uploads.
- A significant security vulnerability is discovered in the Cloudinary integration.
- There are widespread performance issues directly attributable to Cloudinary.

## 2. Rollback Steps

### Step 1: Revert to the Local Storage Git Branch

A git branch named `pre-cloudinary-integration` should be maintained with the code before the Cloudinary integration.

1.  Check out the `pre-cloudinary-integration` branch:
    ```bash
    git checkout pre-cloudinary-integration
    ```
2.  Merge this branch into `main`, resolving any conflicts in favor of the local storage implementation.
    ```bash
    git checkout main
    git merge pre-cloudinary-integration
    ```

### Step 2: Database Migration

The database will contain a mix of Cloudinary URLs and local file paths. A script is needed to convert the Cloudinary URLs back to the local file path format.

**Note:** This step assumes that the local files were not deleted after the migration to Cloudinary. If they were, they would need to be restored from a backup.

1.  **Create a rollback migration script:** This script should:
    -   Connect to the database.
    -   Iterate through the `users` and `clubs` tables.
    -   For each `profile_picture_url` and `image_url` that is a Cloudinary URL, convert it back to a local path (e.g., `/static/profile_pics/...`). This might involve parsing the public_id from the Cloudinary URL.
    -   Update the database with the new local paths.

2.  **Run the rollback script.**

### Step 3: Redeploy

Deploy the updated application to the production environment.

### Step 4: Environment Variables

Remove the Cloudinary-related environment variables from the production environment to prevent any accidental connections to the service.

-   `CLOUDINARY_CLOUD_NAME`
-   `CLOUDINARY_API_KEY`
-   `CLOUDINARY_API_SECRET` 