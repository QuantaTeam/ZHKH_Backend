package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	_ "go.uber.org/automaxprocs"
	"go.uber.org/zap"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/celery"
	"github.com/QuantaTeam/ZHKH_Backend/gerda/config"
	postgres "github.com/QuantaTeam/ZHKH_Backend/gerda/postgres"
	"github.com/QuantaTeam/ZHKH_Backend/gerda/slog"
)

const devLogger = "DEV_LOGGER"

func HandleSignals() {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	sig := <-sigs
	log.Printf("received %s - exiting\n", sig)
	os.Exit(0)
}

func main() {
	log.Println("starting myapp")
	go HandleSignals()

	var logger *zap.Logger
	var err error
	devLogger := os.Getenv(devLogger)
	if devLogger == "true" {
		logger, err = slog.Dev()
	} else {
		logger, err = slog.Prod()
	}
	if err != nil {
		log.Fatalf("failed to initialize logger: %v\n", err)
	}

	conf, err := config.Read()
	if err != nil {
		log.Panicf("failed to read config: %v\n", err)
	}

	rdb, err := postgres.OpenDB()
	if err != nil {
		log.Panicf("could not open pg connection")
	}

	celery.Serve(logger, rdb, conf)
	logger.Info("main exited")
}
