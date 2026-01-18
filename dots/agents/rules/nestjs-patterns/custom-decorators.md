# Custom Decorators (Generic)

- Create parameter decorators to extract commonly needed values
- Use `createParamDecorator()` from `@nestjs/common`
- Examples: extract current user, tenant ID, API key, etc.

```typescript
export const CurrentUser = createParamDecorator(
  (data: unknown, context: ExecutionContext) => {
    const request = context.switchToHttp().getRequest();
    return request.user;
  },
);

// Usage: @CurrentUser() user: UserObject
```
