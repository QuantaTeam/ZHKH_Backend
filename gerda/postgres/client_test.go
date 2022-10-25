package db

import (
	"testing"

	sq "github.com/Masterminds/squirrel"
	"github.com/barklan/cto/pkg/postgres/models"
	_ "github.com/lib/pq"
)

func TestClient(t *testing.T) {
	tx := dbx.MustBegin()
	tx.MustExec(`
insert into client(id, tg_nick, personal_chat, email) values
($1, $2, $3, $4);`,
		"27e9f831-4679-47c8-a64f-f7c8d0cb15ba",
		"barklan",
		342621688,
		"qufiwefefwoyn@gmail.com",
	)

	err := tx.Commit()
	if err != nil {
		panic("failed to commit transaction")
	}

	clients := []models.Client{}

	statement, _, err := sq.Select("*").From("client").ToSql()
	if err != nil {
		panic("sql generation failed")
	}

	err = dbx.Select(&clients, statement)
	if err != nil {
		panic(err)
	}

	barklan := clients[0]
	if barklan.TGNick.String != "barklan" {
		t.Errorf("Got %v want %v", barklan.TGNick, "barklan")
	}
}
