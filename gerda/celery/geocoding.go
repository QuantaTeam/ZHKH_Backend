package celery

import (
	"database/sql"
	"fmt"
	"sync"
	"time"

	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	"go.uber.org/zap"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/config"
)

type ApplicationGeo struct {
	ID             int64          `db:"id"`
	Adress         string         `db:"Адрес проблемы"`
	GeoCoordinates sql.NullString `db:"geo_coordinates"`
}

type GeoData struct {
	ID          int64   `db:"id"`
	ShortAdress string  `db:"short_address"`
	XGeo        float64 `db:"x_geo"`
	YGeo        float64 `db:"y_geo"`
}

func geocode(logger *zap.Logger, rdb *sqlx.DB, conf *config.Config, period time.Duration) {
	// ticker := time.NewTicker(period)
	applicationsWithoutGeo := make([]ApplicationGeo, 0)
	// for range ticker.C {
	for {
		if !conf.GeocodeTaskEnabled {
			logger.Warn("geocode task disabled, skipping")
			continue
		}
		query := fmt.Sprintf(`--sql
            select application.id, application."Адрес проблемы", application.geo_coordinates from application
            where application.geo_coordinates is NULL and application.geo_not_found is NULL
            limit %d`, conf.SimultaneousGeocodeUpdates)
		if err := rdb.Select(&applicationsWithoutGeo, query); err != nil {
			logger.Error("could not get project from db", zap.Error(err))
			continue
		}
		if len(applicationsWithoutGeo) == 0 {
			logger.Info("all applications are already geocoded, exiting")
			continue
		}

		tx, err := rdb.Begin()
		if err != nil {
			logger.Error("failed to create db transaction", zap.Error(err))
			continue
		}

		var wg sync.WaitGroup
		for _, applicationIter := range applicationsWithoutGeo {
			application := applicationIter
			wg.Add(1)
			go func() {
				defer wg.Done()
				var geoData GeoData
				if err = rdb.Get(
					&geoData,
					"select x_geo, y_geo from moscow_geo where short_address = $1",
					application.Adress,
				); err != nil {
					logger.Error("address lookup error", zap.Error(err))
					update := "update application set geo_not_found = true where application.id = $1"
					if _, err = tx.Exec(update, application.ID); err != nil {
						logger.Error("failed set geo_not_found flag", zap.Error(err))
						if e := tx.Rollback(); e != nil {
							logger.Error("failed to rollback transaction", zap.Error(err))
						}
					}
					return
				}
				coordinatesFloats := make([]float64, 2)
				coordinatesFloats[0] = geoData.XGeo
				coordinatesFloats[1] = geoData.YGeo

				update := "update application set geo_coordinates = $1 where application.id = $2"
				if _, err = tx.Exec(update, pq.Array(coordinatesFloats), application.ID); err != nil {
					logger.Error("failed to update geo coordinates", zap.Error(err))
					if e := tx.Rollback(); e != nil {
						logger.Error("failed to rollback transaction", zap.Error(err))
					}
					return
				}
			}()
		}
		wg.Wait()
		if err := tx.Commit(); err != nil {
			logger.Error("failed to commit tx", zap.Error(err))
			continue
		}
		logger.Info("batch update of geo coordinates successful")
	}
}
