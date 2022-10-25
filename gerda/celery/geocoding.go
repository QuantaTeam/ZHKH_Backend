package celery

import (
	"database/sql"
	"encoding/json"
	"io"
	"net/http"
	"time"

	"github.com/jmoiron/sqlx"
	"go.uber.org/zap"

	"github.com/QuantaTeam/ZHKH_Backend/gerda/config"
)

type YandexGeoCodeResp struct {
	Response struct {
		GeoObjectCollection struct {
			MetaDataProperty struct {
				GeocoderResponseMetaData struct {
					Request string `json:"request,omitempty"`
					Results string `json:"results,omitempty"`
					Found   string `json:"found,omitempty"`
				} `json:"GeocoderResponseMetaData,omitempty"`
			} `json:"metaDataProperty,omitempty"`
			FeatureMember []struct {
				GeoObject struct {
					MetaDataProperty struct {
						GeocoderMetaData struct {
							Precision string `json:"precision,omitempty"`
							Text      string `json:"text,omitempty"`
							Kind      string `json:"kind,omitempty"`
							Address   struct {
								CountryCode string `json:"country_code,omitempty"`
								Formatted   string `json:"formatted,omitempty"`
								PostalCode  string `json:"postal_code,omitempty"`
								Components  []struct {
									Kind string `json:"kind,omitempty"`
									Name string `json:"name,omitempty"`
								} `json:"Components,omitempty"`
							} `json:"Address,omitempty"`
							AddressDetails struct {
								Country struct {
									AddressLine        string `json:"AddressLine,omitempty"`
									CountryNameCode    string `json:"CountryNameCode,omitempty"`
									CountryName        string `json:"CountryName,omitempty"`
									AdministrativeArea struct {
										AdministrativeAreaName string `json:"AdministrativeAreaName,omitempty"`
										Locality               struct {
											LocalityName string `json:"LocalityName,omitempty"`
											Thoroughfare struct {
												ThoroughfareName string `json:"ThoroughfareName,omitempty"`
												Premise          struct {
													PremiseNumber string `json:"PremiseNumber,omitempty"`
													PostalCode    struct {
														PostalCodeNumber string `json:"PostalCodeNumber,omitempty"`
													} `json:"PostalCode,omitempty"`
												} `json:"Premise,omitempty"`
											} `json:"Thoroughfare,omitempty"`
										} `json:"Locality,omitempty"`
									} `json:"AdministrativeArea,omitempty"`
								} `json:"Country,omitempty"`
							} `json:"AddressDetails,omitempty"`
						} `json:"GeocoderMetaData,omitempty"`
					} `json:"metaDataProperty,omitempty"`
					Name        string `json:"name,omitempty"`
					Description string `json:"description,omitempty"`
					BoundedBy   struct {
						Envelope struct {
							LowerCorner string `json:"lowerCorner,omitempty"`
							UpperCorner string `json:"upperCorner,omitempty"`
						} `json:"Envelope,omitempty"`
					} `json:"boundedBy,omitempty"`
					Point struct {
						Pos string `json:"pos,omitempty"`
					} `json:"Point,omitempty"`
				} `json:"GeoObject,omitempty"`
			} `json:"featureMember,omitempty"`
		} `json:"GeoObjectCollection,omitempty"`
	} `json:"response,omitempty"`
}

type ApplicationGeo struct {
	ID             int64          `db:"id"`
	Adress         string         `db:"Адрес проблемы"`
	GeoCoordinates sql.NullString `db:"geo_coordinates"`
}

// $.response.[0].GeoObject.Point.pos
func geocode(logger *zap.Logger, rdb *sqlx.DB, conf *config.Config, period time.Duration) {
	ticker := time.NewTicker(period)
	applicationsWithoutGeo := make([]ApplicationGeo, 0)
	for range ticker.C {
		query := `--sql
            select application.id, application."Адрес проблемы", application.geo_coordinates from application
            where application.geo_coordinates is NULL
            limit 1`
		if err := rdb.Select(&applicationsWithoutGeo, query); err != nil {
			logger.Error("could not get project from db", zap.Error(err))
			return
		}
		if len(applicationsWithoutGeo) == 0 {
			logger.Info("all applications are already geocoded, exiting")
			return
		}

		client := &http.Client{}

		for _, application := range applicationsWithoutGeo {
			req, err := http.NewRequest(http.MethodGet, "https://geocode-maps.yandex.ru/1.x/", nil)
			if err != nil {
				logger.Error("failed to construct external request for geocoding", zap.Error(err))
				return
			}
			q := req.URL.Query()
			q.Add("apikey", conf.YandexGeoAPIKey)
			q.Add("format", "json")
			q.Add("geocode", application.Adress)
			req.URL.RawQuery = q.Encode()
			resp, err := client.Do(req)
			if err != nil {
				logger.Info("Errored when sending request to the server")
				return
			}

			defer resp.Body.Close()
			responseBody, err := io.ReadAll(resp.Body)
			if err != nil {
				logger.Error("failed to read response body", zap.Error(err))
				return
			}
			if resp.StatusCode != 200 {
				logger.Error("Yandex geocode non 200", zap.Int("code", resp.StatusCode))
				return
			}
			var respStruct YandexGeoCodeResp
			err = json.Unmarshal(responseBody, &respStruct)
			if err != nil {
				logger.Error("failed to unmarshal json", zap.Error(err))
				return
			}
			coordinates := respStruct.Response.GeoObjectCollection.FeatureMember[0].GeoObject.Point.Pos

			logger.Info("opening tx for geocoding", zap.Int("number", len(applicationsWithoutGeo)))
			tx, err := rdb.Begin()
			if err != nil {
				logger.Error("failed to create db transaction", zap.Error(err))
				return
			}
			update := "update application set geo_coordinates = $1 where application.id = $2"
			if _, err = tx.Exec(update, coordinates, application.ID); err != nil {
				logger.Error("failed to update geo coordinates", zap.Error(err))
				if e := tx.Rollback(); e != nil {
					logger.Error("failed to rollback transaction", zap.Error(err))
				}
				return
			}
			if err := tx.Commit(); err != nil {
				logger.Error("failed to commit tx", zap.Error(err))
				return
			}
			logger.Info("One update of coordinates successful", zap.Int64("application_id", application.ID))
		}

	}
}
