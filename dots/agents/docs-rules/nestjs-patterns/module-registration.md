# Module Registration (Generic)

- Import required modules: `MongooseModule`, `TypeOrmModule`, etc.
- Declare controllers, providers, and other module components
- Export services and schemas for other modules to use

```typescript
@Module({
  imports: [
    MongooseModule.forFeature([{ name: Feature.name, schema: FeatureSchema }]),
  ],
  controllers: [FeatureController],
  providers: [FeatureService],
  exports: [MongooseModule, FeatureService],
})
export class FeatureModule {}
```
