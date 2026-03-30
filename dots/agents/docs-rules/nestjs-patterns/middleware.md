# Middleware Pattern (Generic)

- Middleware runs for all requests before guards/interceptors
- Common uses: logging, CORS setup, sanitization, rate limiting
- Register in `AppModule.configure(consumer)`

```typescript
@Injectable()
export class LoggingMiddleware implements NestMiddleware {
  use(req: Request, res: Response, next: NextFunction) {
    console.log(`${req.method} ${req.path}`);
    next();
  }
}
```
