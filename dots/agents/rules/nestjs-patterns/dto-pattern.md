# DTO Pattern (Generic)

- Use class-based DTOs with decorators for validation
- Popular libraries: `class-validator`, `class-transformer`
- DTOs validate input data at HTTP boundary
- Can be composed using `@nestjs/mapped-types` utilities: `PartialType`, `OmitType`, `PickType`
- Pattern: `CreateFeatureDTO` → `UpdateFeatureDTO extends PartialType(...)`
