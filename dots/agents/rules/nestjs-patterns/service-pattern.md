# Service Pattern (Generic)

- Services contain business logic and data access
- Injected into controllers via constructor
- Use `@Injectable()` decorator
- Database operations abstracted away from controllers
- Dependency injection via constructor parameters

```typescript
@Injectable()
export class FeatureService {
  constructor(
    // Inject dependencies (models, services, etc.)
    private otherService: OtherService,
  ) {}

  // Public methods for business logic
  async create(data: CreateDTO) {}
  async update(id: string, data: UpdateDTO) {}
  async delete(id: string) {}
}
```
