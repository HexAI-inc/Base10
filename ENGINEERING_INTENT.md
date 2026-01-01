# ENGINEERING_INTENT.md

## Role and Responsibility
As the Senior Backend Engineer and owner of the Base10 backend, my responsibility is to ensure the system is correct, stable, scalable, secure, and production-ready. I take full ownership of the codebase, its architecture, and its deployment.

## Project Goals
- Provide a robust, offline-first education platform for rural African students.
- Ensure high availability and performance of API endpoints.
- Maintain data integrity and security.
- Support seamless synchronization between offline clients and the central server.
- Integrate AI capabilities to enhance the learning experience.

## Non-negotiable Engineering Standards
- **Clear Project Structure**: Adhere to a consistent and logical directory structure.
- **Separation of Concerns**: Keep business logic in service layers, data models in the models layer, and API routing in the controllers/api layer.
- **Strong Input Validation**: Use Pydantic schemas for all incoming data.
- **Centralized Error Handling**: Implement a consistent error handling strategy across the application.
- **Secure Authentication and Authorization**: Use JWT-based authentication and role-based access control.
- **Environment-based Configuration**: Manage all configuration through environment variables.
- **Proper Logging**: Use the standard logging library; no `print` statements in production code.
- **Consistent API Behavior**: Ensure predictable responses and proper HTTP status codes.
- **Scalable and Maintainable Design**: Write clean, documented, and testable code.

## Architectural Decisions and Assumptions
- **FastAPI**: Chosen for its performance and ease of use with Pydantic.
- **SQLAlchemy**: Used as the ORM for database interactions.
- **Alembic**: Used for database migrations.
- **PostgreSQL**: Primary database for production.
- **Redis**: Used for caching and state management (e.g., SMS sessions).
- **Offline-First**: The system is designed to handle intermittent connectivity, with long-lived tokens and delta sync capabilities.

## Rules That Must Not Be Violated
- No business logic in API routers.
- No direct database access from API routers (use services or repositories if applicable, though currently services are used).
- All new features must include tests.
- No hardcoded secrets or configuration.
- All API changes must be backward compatible unless a major version bump is justified.
