-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.9.3
-- PostgreSQL version: 13.0
-- Project Site: pgmodeler.io
-- Model Author: ---

-- Database creation must be performed outside a multi lined SQL file. 
-- These commands were put in this file only as a convenience.
-- 
-- object: new_database | type: DATABASE --
-- DROP DATABASE IF EXISTS new_database;
CREATE DATABASE new_database;
-- ddl-end --


-- object: public."Team" | type: TABLE --
-- DROP TABLE IF EXISTS public."Team" CASCADE;
CREATE TABLE public."Team" (
	"Id" varchar(5) NOT NULL,
	"Name" varchar(40),
	"Id_Coach" varchar(5),
	"Code_region" varchar(5) NOT NULL,
	CONSTRAINT "Team_pk" PRIMARY KEY ("Id")

);
-- ddl-end --
ALTER TABLE public."Team" OWNER TO postgres;
-- ddl-end --

-- object: public."Player" | type: TABLE --
-- DROP TABLE IF EXISTS public."Player" CASCADE;
CREATE TABLE public."Player" (
	"Id" varchar(5) NOT NULL,
	"Name" varchar(40) NOT NULL,
	"Id_Team" varchar(5) NOT NULL,
	"Squad_number" integer NOT NULL,
	"Position" varchar(5) NOT NULL,
	"Birthdate" date NOT NULL,
	"Height" numeric(2,2) NOT NULL,
	"Weight" integer NOT NULL,
	"University" varchar(40),
	CONSTRAINT "Player_pk" PRIMARY KEY ("Id")

);
-- ddl-end --
ALTER TABLE public."Player" OWNER TO postgres;
-- ddl-end --

-- object: public."Match" | type: TABLE --
-- DROP TABLE IF EXISTS public."Match" CASCADE;
CREATE TABLE public."Match" (
	"Code" varchar(5) NOT NULL,
	"Team1" varchar(5) NOT NULL,
	"Team2" varchar(5) NOT NULL,
	"Id_season" varchar(5) NOT NULL,
	"Result1" integer NOT NULL,
	"Result2" integer NOT NULL,
	CONSTRAINT "Match_pk" PRIMARY KEY ("Code")

);
-- ddl-end --
ALTER TABLE public."Match" OWNER TO postgres;
-- ddl-end --

-- object: public."Place" | type: TABLE --
-- DROP TABLE IF EXISTS public."Place" CASCADE;
CREATE TABLE public."Place" (
	"Id" varchar(5) NOT NULL,
	"City" varchar(20) NOT NULL,
	"Stadium" varchar(30) NOT NULL,
	CONSTRAINT "Place_pk" PRIMARY KEY ("Id")

);
-- ddl-end --
ALTER TABLE public."Place" OWNER TO postgres;
-- ddl-end --

-- object: public."Participe" | type: TABLE --
-- DROP TABLE IF EXISTS public."Participe" CASCADE;
CREATE TABLE public."Participe" (
	"Id_Team" varchar(5) NOT NULL,
	"Code_Match" varchar(5) NOT NULL,
	"Date" date NOT NULL,
	"Basket" integer NOT NULL,
	"Bounce" integer NOT NULL,
	"Point" integer NOT NULL
);
-- ddl-end --
ALTER TABLE public."Participe" OWNER TO postgres;
-- ddl-end --

-- object: public."Coach" | type: TABLE --
-- DROP TABLE IF EXISTS public."Coach" CASCADE;
CREATE TABLE public."Coach" (
	"Id" varchar(5) NOT NULL,
	"Name" varchar(40) NOT NULL,
	CONSTRAINT "Coach_pk" PRIMARY KEY ("Id")

);
-- ddl-end --
ALTER TABLE public."Coach" OWNER TO postgres;
-- ddl-end --

-- object: public."Happen" | type: TABLE --
-- DROP TABLE IF EXISTS public."Happen" CASCADE;
CREATE TABLE public."Happen" (
	"Id_Place" varchar(5) NOT NULL,
	"Code_Match" varchar(5) NOT NULL
);
-- ddl-end --
ALTER TABLE public."Happen" OWNER TO postgres;
-- ddl-end --

-- object: "Team_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Player" DROP CONSTRAINT IF EXISTS "Team_fk" CASCADE;
ALTER TABLE public."Player" ADD CONSTRAINT "Team_fk" FOREIGN KEY ("Id_Team")
REFERENCES public."Team" ("Id") MATCH FULL
ON DELETE RESTRICT ON UPDATE CASCADE;
-- ddl-end --

-- object: "Coach_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Team" DROP CONSTRAINT IF EXISTS "Coach_fk" CASCADE;
ALTER TABLE public."Team" ADD CONSTRAINT "Coach_fk" FOREIGN KEY ("Id_Coach")
REFERENCES public."Coach" ("Id") MATCH FULL
ON DELETE SET NULL ON UPDATE CASCADE;
-- ddl-end --

-- object: "Team_uq" | type: CONSTRAINT --
-- ALTER TABLE public."Team" DROP CONSTRAINT IF EXISTS "Team_uq" CASCADE;
ALTER TABLE public."Team" ADD CONSTRAINT "Team_uq" UNIQUE ("Id_Coach");
-- ddl-end --

-- object: public."Season" | type: TABLE --
-- DROP TABLE IF EXISTS public."Season" CASCADE;
CREATE TABLE public."Season" (
	"Id" varchar(5) NOT NULL,
	"Name" varchar(40) NOT NULL,
	CONSTRAINT "Season_pk" PRIMARY KEY ("Id")

);
-- ddl-end --
ALTER TABLE public."Season" OWNER TO postgres;
-- ddl-end --

-- object: public."Region" | type: TABLE --
-- DROP TABLE IF EXISTS public."Region" CASCADE;
CREATE TABLE public."Region" (
	"Code" varchar(5) NOT NULL,
	"Name" varchar(40) NOT NULL,
	CONSTRAINT "Region_pk" PRIMARY KEY ("Code")

);
-- ddl-end --
ALTER TABLE public."Region" OWNER TO postgres;
-- ddl-end --

-- object: "Code_region_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Team" DROP CONSTRAINT IF EXISTS "Code_region_fk" CASCADE;
ALTER TABLE public."Team" ADD CONSTRAINT "Code_region_fk" FOREIGN KEY ("Code_region")
REFERENCES public."Region" ("Code") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Team1_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Match" DROP CONSTRAINT IF EXISTS "Team1_fk" CASCADE;
ALTER TABLE public."Match" ADD CONSTRAINT "Team1_fk" FOREIGN KEY ("Team1")
REFERENCES public."Participe" ("Id_Team") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Team2_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Match" DROP CONSTRAINT IF EXISTS "Team2_fk" CASCADE;
ALTER TABLE public."Match" ADD CONSTRAINT "Team2_fk" FOREIGN KEY ("Team2")
REFERENCES public."Participe" ("Id_Team") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Id_season_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Match" DROP CONSTRAINT IF EXISTS "Id_season_fk" CASCADE;
ALTER TABLE public."Match" ADD CONSTRAINT "Id_season_fk" FOREIGN KEY ("Id_season")
REFERENCES public."Season" ("Id") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Match_code_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Participe" DROP CONSTRAINT IF EXISTS "Match_code_fk" CASCADE;
ALTER TABLE public."Participe" ADD CONSTRAINT "Match_code_fk" FOREIGN KEY ("Code_Match")
REFERENCES public."Match" ("Code") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Team_name_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Participe" DROP CONSTRAINT IF EXISTS "Team_name_fk" CASCADE;
ALTER TABLE public."Participe" ADD CONSTRAINT "Team_name_fk" FOREIGN KEY ("Id_Team")
REFERENCES public."Team" ("Id") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Match_code_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Happen" DROP CONSTRAINT IF EXISTS "Match_code_fk" CASCADE;
ALTER TABLE public."Happen" ADD CONSTRAINT "Match_code_fk" FOREIGN KEY ("Code_Match")
REFERENCES public."Match" ("Code") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: "Place_id_fk" | type: CONSTRAINT --
-- ALTER TABLE public."Happen" DROP CONSTRAINT IF EXISTS "Place_id_fk" CASCADE;
ALTER TABLE public."Happen" ADD CONSTRAINT "Place_id_fk" FOREIGN KEY ("Id_Place")
REFERENCES public."Place" ("Id") MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


