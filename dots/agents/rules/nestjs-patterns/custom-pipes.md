# Custom Pipes (Generic)

- Pipes transform and validate data
- Implement `PipeTransform` interface
- Used for parameter validation (MongoDB ID format, enum matching, etc.)

```typescript
@Injectable()
export class ValidateMongoId implements PipeTransform<string, string> {
  transform(value: any): string {
    if (!isValidMongoId(value)) {
      throw new BadRequestException("Invalid ID");
    }
    return value;
  }
}

// Usage: @Param('id', ValidateMongoId) id: string
```
