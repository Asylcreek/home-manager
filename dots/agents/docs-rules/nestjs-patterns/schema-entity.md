# Schema/Entity Pattern (Generic)

- Define data models using ORM/ODM decorators (`@Entity`, `@Schema`, `@Table`, etc.)
- Add validation rules to model properties
- Define relationships (foreign keys, references)
- Create TypeScript type definitions that extend the model

Examples:

- **Mongoose**: `@Schema()` + `@Prop()` decorators
- **TypeORM**: `@Entity()` + `@Column()` decorators
- **Prisma**: `.prisma` schema definitions
