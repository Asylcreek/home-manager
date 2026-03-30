# Response Interceptor Pattern (Generic)

- Interceptors run on every response
- Standardize response format across all endpoints
- Add metadata (timestamp, version, etc.)
- Never ask developers to manually wrap responses

```typescript
@Injectable()
export class ResponseInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler) {
    return next.handle().pipe(
      map((data) => ({
        success: true,
        data,
        timestamp: new Date(),
      })),
    );
  }
}
```
