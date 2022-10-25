package models

import "database/sql"

type Client struct {
	ID           string         `db:"id"`
	Active       bool           `db:"active"`
	TGNick       sql.NullString `db:"tg_nick"`
	PersonalChat sql.NullInt64  `db:"personal_chat"`
	Email        string         `db:"email"`
}

type Project struct {
	ID          string         `db:"id"`
	Active      bool           `db:"active"`
	ClientID    string         `db:"client_id"`
	PrettyTitle sql.NullString `db:"pretty_title"`
	SecretKey   string         `db:"secret_key"`
}

type Chat struct {
	ID        int64  `db:"id"`
	Active    bool   `db:"active"`
	ProjectID string `db:"project_id"`
}
