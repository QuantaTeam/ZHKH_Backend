package celery

import (
	"os"
	"sync"
	"time"

	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/config"
)

func Serve(logger *zap.Logger, rdb *sqlx.DB, conf *config.Config) {
	var wg sync.WaitGroup
	wg.Add(1)

	go func() {
		defer func() {
			rdb.Close()
			os.Exit(1)
			wg.Done()
		}()
		period := time.Duration(conf.GeocodeIntervalSeconds) * time.Second
		geocode(logger, rdb, conf, period)
	}()
	wg.Wait()
}
