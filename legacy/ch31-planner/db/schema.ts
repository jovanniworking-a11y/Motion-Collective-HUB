import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';
export const records = sqliteTable('planning_records', {
  id: text('id').primaryKey(), value: text('value').notNull(), revision: integer('revision').notNull().default(1),
});
