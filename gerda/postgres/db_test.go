package db

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"testing"
	"time"

	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/ory/dockertest/v3"
	"github.com/ory/dockertest/v3/docker"

	_ "github.com/golang-migrate/migrate/v4/source/file"
)

var dbx *sqlx.DB // nolint:gochecknoglobals

func PrepareTestDB() (*sql.DB, *dockertest.Pool, *dockertest.Resource) {
	var db *sql.DB
	pool, err := dockertest.NewPool("")
	if err != nil {
		log.Fatalf("Could not connect to docker: %s", err)
	}

	// pulls an image, creates a container based on it and runs it
	resource, err := pool.RunWithOptions(&dockertest.RunOptions{
		Repository: "postgres",
		Tag:        "14",
		Env: []string{
			"POSTGRES_PASSWORD=postgres",
			"POSTGRES_USER=postgres",
			"POSTGRES_DB=app",
			"listen_addresses = '*'",
		},
	}, func(config *docker.HostConfig) {
		// set AutoRemove to true so that stopped container goes away by itself
		config.AutoRemove = true
		config.RestartPolicy = docker.RestartPolicy{Name: "no"}
	})
	if err != nil {
		log.Fatalf("Could not start resource: %s", err)
	}

	hostAndPort := resource.GetHostPort("5432/tcp")
	databaseUrl := fmt.Sprintf("postgres://postgres:postgres@%s/app?sslmode=disable",
		hostAndPort)

	log.Printf("connecting to database on %q\n", databaseUrl)

	resource.Expire(60) // Tell docker to hard kill the container in 120 seconds

	// exponential backoff-retry
	pool.MaxWait = 120 * time.Second
	if err = pool.Retry(func() error {
		db, err = sql.Open("postgres", databaseUrl)
		if err != nil {
			return err
		}
		return db.Ping()
	}); err != nil {
		log.Fatalf("Could not connect to docker: %s", err)
	}

	// Migrate
	driver, err := postgres.WithInstance(db, &postgres.Config{})
	migrationManager, err := migrate.NewWithDatabaseInstance(
		"file://../../db/migrations",
		"postgres", driver)
	err = migrationManager.Up()
	if err != nil {
		log.Fatal(err)
	}

	return db, pool, resource
}

func TestMain(m *testing.M) {
	db, pool, resource := PrepareTestDB()
	dbx = sqlx.NewDb(db, "postgres")

	// Run tests
	code := m.Run()

	// You can't defer this because os.Exit doesn't care for defer
	if err := pool.Purge(resource); err != nil {
		log.Fatalf("Could not purge resource: %s", err)
	}

	os.Exit(code)
}
