# Testing Pattern (Generic)

- Test files colocate with source: `feature.service.spec.ts` in same directory as `feature.service.ts`
- Use `@nestjs/testing` module for test setup
- Mock dependencies via `Test.createTestingModule()`
- Test services and business logic, not implementation details

```typescript
describe("FeatureService", () => {
  let service: FeatureService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [FeatureService, MockService],
    }).compile();
    service = module.get<FeatureService>(FeatureService);
  });

  it("should work", async () => {
    const result = await service.create({});
    expect(result).toBeDefined();
  });
});
```
