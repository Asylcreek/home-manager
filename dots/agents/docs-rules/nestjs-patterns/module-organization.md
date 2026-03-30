# Module/Feature Organization (Generic)

NestJS projects are organized into self-contained modules. Each feature typically includes:

- **Controller** - Handles HTTP requests and delegates to services
- **Service** - Contains business logic and data operations
- **Schema/Entity** - Data model definition (Mongoose, TypeORM, etc.)
- **DTO** - Data transfer objects for request/response validation
- **Module** - Brings components together with imports and exports
- **Tests** - Unit tests for services
- **Optional**: Guards, Interceptors, Pipes, Decorators
