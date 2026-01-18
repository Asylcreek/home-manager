# Dependency Injection (Generic)

- NestJS uses constructor-based dependency injection
- Decorators: `@Inject()`, `@Optional()`, `@InjectModel()`, etc.
- Dependencies are automatically resolved by the container
- Never manually instantiate classes with `new` (use DI instead)

```typescript
@Injectable()
export class FeatureService {
  constructor(
    private otherService: OtherService, // Auto-injected
    @Optional() private optionalService?: OptionalService,
    @Inject("CONFIG") private config: ConfigObject,
  ) {}
}
```
