drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  param integer not null,
  answer integer not null
);