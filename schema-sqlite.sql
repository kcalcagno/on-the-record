create table game (
  game_id integer primary key,
  opponent text not null,
  short_name text not null,
  conference integer not null default 0,
  nd_score integer,
  opp_score integer
);

create table poster (
  poster_id integer primary key autoincrement,
  poster_name text not null,
  name_key text unique not null
);

create table prediction (
  game_id integer not null references game(game_id),
  poster_id integer not null references poster(poster_id),
  nd_score integer not null,
  opp_score integer not null,
  primary key (game_id, poster_id),
  check (nd_score <> opp_score)
);
