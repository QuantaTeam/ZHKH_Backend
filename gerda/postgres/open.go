package db

import (
	"fmt"

	"github.com/caarlos0/env"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
)

type PGConnectionData struct {
	DB       string `env:"POSTGRES_DB"`
	Password string `env:"POSTGRES_PASSWORD"`
	User     string `env:"POSTGRES_USER"`
	Host     string `env:"POSTGRES_SERVER"`
}

func OpenDB() (*sqlx.DB, error) {
	cfg := PGConnectionData{}
	err := env.Parse(&cfg)
	if err != nil {
		return &sqlx.DB{}, err
	}

	db, err := sqlx.Connect(
		"postgres",
		fmt.Sprintf(
			"postgres://%s:%s@%s:5432/%s?sslmode=disable",
			cfg.User,
			cfg.Password,
			cfg.Host,
			cfg.DB,
		),
	)
	return db, err
}
