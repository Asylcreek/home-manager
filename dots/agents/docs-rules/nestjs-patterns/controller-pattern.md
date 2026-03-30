# Controller Pattern (Generic)

- Controllers are thin - only handle routing and parameter extraction
- Delegate all business logic to services
- Use decorators: `@Get()`, `@Post()`, `@Patch()`, `@Delete()`
- Extract parameters via `@Param()`, `@Body()`, `@Query()`, `@Headers()`
- Apply guards/interceptors for authorization and cross-cutting concerns
- Never wrap responses manually - use interceptors

```typescript
@Controller("features")
export class FeatureController {
  constructor(private featureService: FeatureService) {}

  @Get()
  async getAll() {
    return await this.featureService.getAll();
  }

  @Post()
  async create(@Body() data: CreateFeatureDTO) {
    return await this.featureService.create(data);
  }

  @Patch(":id")
  async update(@Param("id") id: string, @Body() data: UpdateFeatureDTO) {
    return await this.featureService.update(id, data);
  }
}
```
