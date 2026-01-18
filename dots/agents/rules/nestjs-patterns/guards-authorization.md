# Guard/Authorization Pattern (Generic)

- Guards control access to endpoints
- Implement `CanActivate` interface
- Stack multiple guards for layered authorization
- Common pattern: Authentication → Role → Permissions

```typescript
@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    return this.validateToken(request.headers.authorization);
  }
}

// Usage
@UseGuards(JwtAuthGuard)
@Controller("admin")
export class AdminController {}
```
