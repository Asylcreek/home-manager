# General Best Practices (Generic)

1. **Keep controllers thin** - They route and delegate to services
2. **Put logic in services** - Services are testable and reusable
3. **Validate at boundaries** - Use DTOs to validate incoming data
4. **Use dependency injection** - Don't instantiate dependencies manually
5. **Handle errors consistently** - Use global exception filter
6. **Test services** - Test business logic in isolation
7. **Use type safety** - Leverage TypeScript for type safety
8. **Follow SOLID principles** - Especially Single Responsibility and Dependency Inversion
9. **Avoid circular dependencies** - Can cause module resolution issues
10. **Use composition over inheritance** - Favor interfaces and composition patterns
