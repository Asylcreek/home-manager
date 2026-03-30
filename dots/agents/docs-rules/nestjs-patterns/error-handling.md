# Error Handling (Generic Pattern)

- Create a custom error class that includes status codes
- Implement a global exception filter to standardize error responses
- Never let raw errors escape - catch and wrap in standardized format
- Log errors appropriately for debugging

```typescript
// Custom error class
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number,
  ) {
    super(message);
  }
}

// Global exception filter
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: any, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const res = ctx.getResponse();

    const statusCode = exception.statusCode || 500;
    const message = exception.message || "Internal Server Error";

    res.status(statusCode).json({
      error: message,
      statusCode,
    });
  }
}
```
